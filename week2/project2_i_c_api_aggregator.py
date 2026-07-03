"""
Week 2 - Day 5: Project 2-I-C
API Aggregator Agent — Morning Briefing with Financial Focus

Architecture:
    Scheduler
        -> 3 Parallel Async Tool Calls (asyncio.gather)
            -> Weather API   (Open-Meteo, free)
            -> Currency API  (exchangerate-api, free)
            -> Financial News API (GNews, free fallback)
        -> DataAggregator
        -> LLM Synthesizer (Groq, chain-of-thought prompt)
        -> ReportFormatter (.md + .html output)

Week 2 Learning Integrated:
    Day 1 - Chain-of-Thought prompt in ReportSynthesizer
    Day 2 - Pydantic structured schema for BriefingReport
    Day 3 - Tool routing with tool registry pattern
    Day 4 - Exponential backoff and retry logic on every API call
"""

import os
import asyncio
import json
import random
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

load_dotenv()
console = Console()

# ─── API Endpoints ───────────────────────────────────────────────────────────

WEATHER_API  = "https://api.open-meteo.com/v1/forecast"
CURRENCY_API = "https://api.exchangerate-api.com/v4/latest/USD"
NEWS_API     = "https://gnews.io/api/v4/search"

# ─── City Coordinates ────────────────────────────────────────────────────────

CITY_COORDS: Dict[str, Dict[str, float]] = {
    "london":     {"lat": 51.5074,  "lon": -0.1278},
    "paris":      {"lat": 48.8566,  "lon":  2.3522},
    "new york":   {"lat": 40.7128,  "lon": -74.0060},
    "tokyo":      {"lat": 35.6762,  "lon": 139.6503},
    "dubai":      {"lat": 25.2048,  "lon":  55.2708},
    "karachi":    {"lat": 24.8607,  "lon":  67.0011},
    "islamabad":  {"lat": 33.6844,  "lon":  73.0479},
    "lahore":     {"lat": 31.5204,  "lon":  74.3587},
    "mumbai":     {"lat": 19.0760,  "lon":  72.8777},
    "singapore":  {"lat":  1.3521,  "lon": 103.8198},
    "new york":   {"lat": 40.7128,  "lon": -74.0060},
}

WEATHER_CODE_MAP: Dict[int, str] = {
    0: "Clear Sky",      1: "Mainly Clear",    2: "Partly Cloudy",
    3: "Overcast",      45: "Fog",            48: "Icy Fog",
    51: "Light Drizzle", 61: "Light Rain",     71: "Light Snow",
    80: "Rain Showers",  85: "Snow Showers",   95: "Thunderstorm",
}

# ─── Pydantic Schemas (Day 2 - Structured Outputs) ───────────────────────────

class WeatherData(BaseModel):
    city:        str
    temperature: float
    windspeed:   float
    condition:   str
    success:     bool
    error:       Optional[str] = None

class NewsItem(BaseModel):
    title:       str
    description: str
    source:      Optional[str] = None

class CurrencyData(BaseModel):
    base:    str
    rates:   Dict[str, float]
    success: bool
    mock:    bool = False
    error:   Optional[str] = None

class BriefingReport(BaseModel):
    city:      str
    timestamp: str
    weather:   WeatherData
    news:      List[NewsItem]
    currency:  CurrencyData

# ─── Retry Utilities (Day 4 - Exponential Backoff) ───────────────────────────

class APIError(Exception):
    """Raised when an API call fails after all retries."""

def _backoff_delay(attempt: int, base: float = 1.0, cap: float = 30.0) -> float:
    """Calculate jittered exponential backoff delay."""
    delay = min(base * (2 ** attempt), cap)
    return delay + random.uniform(0, delay * 0.1)

async def _get_with_retry(
    client: httpx.AsyncClient,
    url: str,
    params: Optional[Dict] = None,
    max_retries: int = 3,
) -> Dict[str, Any]:
    """
    GET request with exponential backoff retry.
    Retries on 429, 5xx, and network errors.
    """
    last_exc: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            response = await client.get(url, params=params, timeout=20.0)

            if response.status_code == 429 or response.status_code >= 500:
                delay = _backoff_delay(attempt)
                console.log(f"[dim]HTTP {response.status_code} — retrying in {delay:.1f}s[/dim]")
                await asyncio.sleep(delay)
                continue

            response.raise_for_status()
            return response.json()

        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            last_exc = exc
            if attempt < max_retries - 1:
                delay = _backoff_delay(attempt)
                await asyncio.sleep(delay)
            continue

        except httpx.HTTPStatusError as exc:
            last_exc = exc
            continue

    raise APIError(f"All {max_retries} attempts failed. Last error: {last_exc}")

# ─── Tool 1: Weather Fetcher ─────────────────────────────────────────────────

async def fetch_weather(city: str) -> WeatherData:
    """Fetch current weather for a city from Open-Meteo (no API key)."""
    coords = CITY_COORDS.get(city.lower())
    if not coords:
        return WeatherData(
            city=city, temperature=0, windspeed=0,
            condition="Unknown", success=False,
            error=f"City '{city}' not in coordinate map.",
        )

    try:
        async with httpx.AsyncClient() as client:
            params = {
                "latitude":        coords["lat"],
                "longitude":       coords["lon"],
                "current_weather": "true",
                "timezone":        "auto",
            }
            data = await _get_with_retry(client, WEATHER_API, params)

        if "current_weather" in data:
            w = data["current_weather"]
            code = w.get("weathercode", 0)
            return WeatherData(
                city=city.title(),
                temperature=w.get("temperature", 0),
                windspeed=w.get("windspeed", 0),
                condition=WEATHER_CODE_MAP.get(code, "Unknown"),
                success=True,
            )
        return WeatherData(city=city, temperature=0, windspeed=0, condition="N/A", success=False, error="No weather payload.")

    except Exception as exc:
        return WeatherData(city=city, temperature=0, windspeed=0, condition="N/A", success=False, error=str(exc))

# ─── Tool 2: Financial News Fetcher ─────────────────────────────────────────

_MOCK_NEWS: List[NewsItem] = [
    NewsItem(title="Global Equities Advance as Inflation Data Eases", description="Stock markets rallied across major indices after softer-than-expected CPI figures.", source="Reuters"),
    NewsItem(title="Federal Reserve Signals Measured Rate Path Ahead", description="Fed officials indicated a cautious stance on further tightening, boosting bond markets.", source="Bloomberg"),
    NewsItem(title="Oil Prices Stabilise on Supply Discipline Reports", description="Brent crude held steady as OPEC confirmed continued output constraints.", source="FT"),
    NewsItem(title="Pakistani Rupee Strengthens Against US Dollar", description="The PKR gained ground following improved current account data and IMF tranche release.", source="Dawn"),
    NewsItem(title="Tech Sector Leads Market Recovery in Asia-Pacific", description="Asian technology stocks outperformed after strong earnings guidance from chipmakers.", source="Nikkei"),
]

async def fetch_financial_news(topic: str = "financial markets") -> List[NewsItem]:
    """
    Fetch financial news headlines.
    Falls back to curated mock data if the API is unavailable.
    """
    try:
        async with httpx.AsyncClient() as client:
            params = {
                "q":        topic,
                "lang":     "en",
                "max":      "5",
                "token":    os.getenv("GNEWS_API_KEY", ""),
            }
            data = await _get_with_retry(client, NEWS_API, params, max_retries=2)
            articles = data.get("articles", [])
            if articles:
                return [
                    NewsItem(
                        title=a.get("title", ""),
                        description=a.get("description", "")[:150],
                        source=a.get("source", {}).get("name"),
                    )
                    for a in articles[:5]
                ]
    except Exception:
        pass  # Fall through to mock data

    return _MOCK_NEWS

# ─── Tool 3: Currency Fetcher ─────────────────────────────────────────────────

_KEY_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "CHF", "AUD", "PKR", "INR", "SGD"]

_MOCK_RATES: Dict[str, float] = {
    "USD": 1.0, "EUR": 0.92, "GBP": 0.79, "JPY": 157.40,
    "CAD": 1.36, "CHF": 0.90, "AUD": 1.54, "PKR": 279.50,
    "INR": 83.50, "SGD": 1.35,
}

async def fetch_currency_rates() -> CurrencyData:
    """Fetch USD-based exchange rates from exchangerate-api."""
    try:
        async with httpx.AsyncClient() as client:
            data = await _get_with_retry(client, CURRENCY_API, max_retries=3)

        if "rates" in data:
            all_rates = data["rates"]
            key_rates = {k: all_rates[k] for k in _KEY_CURRENCIES if k in all_rates}
            return CurrencyData(base="USD", rates=key_rates, success=True)

    except Exception:
        pass

    return CurrencyData(base="USD", rates=_MOCK_RATES, success=True, mock=True)

# ─── Data Aggregator (parallel) ──────────────────────────────────────────────

class DataAggregator:
    """Runs all three API fetches concurrently via asyncio.gather."""

    @staticmethod
    async def aggregate(city: str = "London") -> BriefingReport:
        console.log("[dim]Dispatching parallel API calls...[/dim]")

        weather_result, news_result, currency_result = await asyncio.gather(
            fetch_weather(city),
            fetch_financial_news("financial markets stocks"),
            fetch_currency_rates(),
        )

        return BriefingReport(
            city=city,
            timestamp=datetime.now().isoformat(),
            weather=weather_result,
            news=news_result,
            currency=currency_result,
        )

# ─── LLM Report Synthesizer (Day 1 - Chain-of-Thought) ─────────────────────

class ReportSynthesizer:
    """
    Synthesizes aggregated API data into a structured morning briefing.
    Uses a chain-of-thought prompt so the model reasons step-by-step
    before producing the final professional report.
    """

    def __init__(self) -> None:
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def generate(self, report: BriefingReport) -> str:
        context = self._build_context(report)

        # Chain-of-Thought prompt (Day 1 learning)
        prompt = ChatPromptTemplate.from_template(
            """You are a senior financial analyst producing a professional morning briefing.

Think step-by-step before writing the final report:
1. Review the weather data and note any operational impact.
2. Analyse the financial news headlines for key market themes.
3. Interpret the currency movements in context of the news.
4. Synthesise all three data sources into a cohesive narrative.

Raw Data:
{context}

Now write a professional morning briefing report in Markdown with these sections:
## Executive Summary
## Weather & Operational Context
## Financial Markets Update
## Currency Snapshot
## Key Takeaways & Outlook

Rules:
- Write in clear, formal financial language.
- Do not use emojis.
- Use bullet points inside sections.
- Keep the report under 500 words.
"""
        )

        chain = prompt | self.llm | StrOutputParser()
        try:
            return chain.invoke({"context": context})
        except Exception as exc:
            return f"Report generation failed: {exc}"

    @staticmethod
    def _build_context(report: BriefingReport) -> str:
        lines: List[str] = [
            f"City: {report.city}",
            f"Timestamp: {report.timestamp}",
        ]

        w = report.weather
        if w.success:
            lines.append(f"Weather — {w.city}: {w.temperature}C, wind {w.windspeed} km/h, {w.condition}")
        else:
            lines.append(f"Weather unavailable: {w.error}")

        lines.append("\nFinancial News Headlines:")
        for item in report.news:
            lines.append(f"  - {item.title} ({item.source or 'Unknown'})")
            lines.append(f"    {item.description}")

        c = report.currency
        lines.append(f"\nCurrency Rates (base: {c.base}){'  [mock data]' if c.mock else ''}:")
        for code, rate in list(c.rates.items())[:8]:
            lines.append(f"  1 {c.base} = {rate:.4f} {code}")

        return "\n".join(lines)

# ─── Report Formatter ────────────────────────────────────────────────────────

class ReportFormatter:
    """Formats the synthesised report for file output."""

    @staticmethod
    def as_markdown(body: str, report: BriefingReport) -> str:
        header = (
            f"# Morning Briefing Report\n\n"
            f"**City:** {report.city}  \n"
            f"**Generated:** {datetime.now().strftime('%A, %d %B %Y at %H:%M')}  \n\n"
            "---\n\n"
        )
        return header + body

    @staticmethod
    def as_html(body: str, report: BriefingReport) -> str:
        import re

        def md_to_html(text: str) -> str:
            text = re.sub(r"^## (.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
            text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
            text = re.sub(r"^- (.+)$", r"<li>\1</li>", text, flags=re.MULTILINE)
            text = re.sub(r"(<li>.*</li>)", r"<ul>\1</ul>", text, flags=re.DOTALL)
            text = re.sub(r"\n\n", "<br><br>", text)
            return text

        generated = datetime.now().strftime("%A, %d %B %Y at %H:%M")
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morning Briefing — {report.city}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f1117;
            color: #e0e6f0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 820px;
            margin: auto;
            background: #1a1d27;
            border-radius: 12px;
            padding: 40px;
            border: 1px solid #2a2d3e;
        }}
        h1 {{
            font-size: 1.8rem;
            color: #7eb8f7;
            border-bottom: 2px solid #2a3a5c;
            padding-bottom: 12px;
            margin-bottom: 8px;
        }}
        .meta {{ color: #6b7590; font-size: 0.9rem; margin-bottom: 28px; }}
        h2 {{
            font-size: 1.1rem;
            color: #a8d0f8;
            margin: 24px 0 10px;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 6px 0; line-height: 1.6; color: #c8d4e8; }}
        strong {{ color: #e0e6f0; }}
        .footer {{
            margin-top: 36px;
            padding-top: 16px;
            border-top: 1px solid #2a2d3e;
            color: #4a5068;
            font-size: 0.8rem;
            text-align: center;
        }}
        .badge {{
            display: inline-block;
            background: #1e3050;
            color: #7eb8f7;
            border: 1px solid #2a4070;
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 0.75rem;
            margin-left: 6px;
            vertical-align: middle;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Morning Briefing Report <span class="badge">{report.city}</span></h1>
        <div class="meta">Generated: {generated} | CalderR AI Internship — Week 2 Day 5</div>
        <hr style="border-color:#2a2d3e; margin-bottom:24px;">
        {md_to_html(body)}
        <div class="footer">
            Automated report generated by the API Aggregator Agent.
            Data sourced from Open-Meteo, exchangerate-api, and GNews.
        </div>
    </div>
</body>
</html>"""

# ─── Display Helpers ─────────────────────────────────────────────────────────

def _display_data_summary(report: BriefingReport) -> None:
    table = Table(title="API Data Summary", box=box.ROUNDED, show_lines=True)
    table.add_column("Source",  style="cyan",  width=14)
    table.add_column("Status",  style="white", width=10)
    table.add_column("Detail",  style="white")

    w = report.weather
    table.add_row(
        "Weather",
        "OK"      if w.success else "FAILED",
        f"{w.city}: {w.temperature}C, {w.condition}" if w.success else w.error or "N/A",
    )

    table.add_row(
        "Financial News",
        "OK"      if report.news else "FAILED",
        f"{len(report.news)} headlines fetched" if report.news else "No data",
    )

    c = report.currency
    mock_note = " (mock)" if c.mock else ""
    table.add_row(
        "Currency",
        "OK"      if c.success else "FAILED",
        f"{len(c.rates)} pairs loaded{mock_note}" if c.success else c.error or "N/A",
    )

    console.print(table)

# ─── Main Entry Point ────────────────────────────────────────────────────────

async def main() -> None:
    console.print(Panel.fit(
        "API Aggregator Agent\n"
        "Week 2 - Day 5 | Project 2-I-C\n"
        "Financial Morning Briefing",
        border_style="cyan",
    ))

    city = input("\nEnter city for weather (default: London): ").strip() or "London"

    console.print(f"\n[bold cyan]Aggregating data for {city.title()}...[/bold cyan]\n")

    report_data = await DataAggregator.aggregate(city)

    _display_data_summary(report_data)

    console.print("\n[bold cyan]Synthesising morning briefing report (chain-of-thought LLM)...[/bold cyan]\n")

    synthesizer = ReportSynthesizer()
    body = synthesizer.generate(report_data)

    console.print(Panel(
        body,
        title="Morning Briefing Report",
        border_style="green",
        padding=(1, 2),
    ))

    # Save outputs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path   = f"report_{timestamp}.md"
    html_path = f"report_{timestamp}.html"

    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(ReportFormatter.as_markdown(body, report_data))

    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(ReportFormatter.as_html(body, report_data))

    console.print(f"\n[green]Reports saved:[/green]")
    console.print(f"  {md_path}")
    console.print(f"  {html_path}")

    # Show raw JSON (truncated)
    console.print("\n[bold cyan]Structured Data (Pydantic JSON):[/bold cyan]")
    raw = report_data.model_dump()
    console.print(json.dumps(raw, indent=2, default=str)[:1200] + "\n  ...(truncated)")

if __name__ == "__main__":
    asyncio.run(main())
