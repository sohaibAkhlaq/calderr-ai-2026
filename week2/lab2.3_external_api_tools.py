"""
Week 2 - Day 4: Lab 2.3 - External API Tools
Integrating real external APIs as tools with error handling
"""

import os
import json
import asyncio
import time
import random
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

load_dotenv()
console = Console()

# ─── Configuration ───

# Free API endpoints (no API key required for demo)
WEATHER_API = "https://api.open-meteo.com/v1/forecast"
NEWS_API = "https://api.currentsapi.services/v1/latest-news"
CURRENCY_API = "https://api.exchangerate-api.com/v4/latest/USD"

# ─── Error Handling Utilities ───

class APIError(Exception):
    """Custom exception for API errors"""
    pass

class RateLimitError(APIError):
    """Exception for rate limit errors"""
    pass

class TimeoutError(APIError):
    """Exception for timeout errors"""
    pass

def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Calculate exponential backoff delay with jitter.
    
    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
    
    Returns:
        float: Delay in seconds
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    # Add jitter (random variation)
    jitter = random.uniform(0, delay * 0.1)
    return delay + jitter

async def call_api_with_retry(
    client: httpx.AsyncClient,
    url: str,
    params: Optional[Dict] = None,
    max_retries: int = 3,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Call API with retry logic and exponential backoff.
    
    Args:
        client: HTTP client
        url: API endpoint
        params: Query parameters
        max_retries: Maximum number of retries
        timeout: Request timeout in seconds
    
    Returns:
        Dict: API response data
    
    Raises:
        APIError: If all retries fail
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            console.log(f"[dim]API Call attempt {attempt + 1}/{max_retries} to {url}[/dim]")
            
            response = await client.get(url, params=params, timeout=timeout)
            
            if response.status_code == 429:
                # Rate limit hit
                delay = exponential_backoff(attempt)
                console.log(f"[yellow]Rate limited. Waiting {delay:.2f}s[/yellow]")
                await asyncio.sleep(delay)
                continue
            
            if response.status_code >= 500:
                # Server error - retry
                delay = exponential_backoff(attempt)
                console.log(f"[yellow]Server error {response.status_code}. Retrying in {delay:.2f}s[/yellow]")
                await asyncio.sleep(delay)
                continue
            
            response.raise_for_status()
            return response.json()
            
        except httpx.TimeoutException as e:
            last_error = TimeoutError(f"Request timeout: {e}")
            console.log(f"[yellow]Timeout on attempt {attempt + 1}[/yellow]")
            if attempt < max_retries - 1:
                delay = exponential_backoff(attempt)
                await asyncio.sleep(delay)
            continue
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                last_error = RateLimitError(f"Rate limit exceeded: {e}")
                continue
            last_error = APIError(f"HTTP error {e.response.status_code}: {e}")
            continue
            
        except Exception as e:
            last_error = APIError(f"Unexpected error: {e}")
            continue
    
    if last_error:
        raise last_error
    raise APIError("All retry attempts failed")

# ─── Tool 1: Weather API ───

@tool
async def get_weather(city: str) -> str:
    """
    Get current weather for a city using Open-Meteo API.
    
    Args:
        city: The city name
    
    Returns:
        str: Weather information
    """
    
    try:
        # Simple city to coordinates mapping (mock)
        city_coords = {
            "london": {"lat": 51.5074, "lon": -0.1278},
            "paris": {"lat": 48.8566, "lon": 2.3522},
            "new york": {"lat": 40.7128, "lon": -74.0060},
            "tokyo": {"lat": 35.6762, "lon": 139.6503},
            "dubai": {"lat": 25.2048, "lon": 55.2708},
            "karachi": {"lat": 24.8607, "lon": 67.0011},
            "islamabad": {"lat": 33.6844, "lon": 73.0479},
            "lahore": {"lat": 31.5204, "lon": 74.3587},
            "mumbai": {"lat": 19.0760, "lon": 72.8777},
            "singapore": {"lat": 1.3521, "lon": 103.8198}
        }
        
        city_lower = city.lower()
        coords = None
        
        for key, value in city_coords.items():
            if key in city_lower or city_lower in key:
                coords = value
                break
        
        if not coords:
            return f"Weather data not available for '{city}'. Try: London, Paris, New York, Tokyo, Dubai, Karachi, Islamabad, Lahore, Mumbai, Singapore"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "current_weather": "true",
                "timezone": "auto"
            }
            
            data = await call_api_with_retry(client, WEATHER_API, params)
            
            if "current_weather" in data:
                weather = data["current_weather"]
                temp = weather.get("temperature", "N/A")
                wind = weather.get("windspeed", "N/A")
                
                # Map weather code to description
                code = weather.get("weathercode", 0)
                weather_map = {
                    0: "Clear",
                    1: "Mainly Clear",
                    2: "Partly Cloudy",
                    3: "Overcast",
                    45: "Fog",
                    51: "Light Drizzle",
                    61: "Rain",
                    71: "Snow",
                    80: "Rain Showers"
                }
                description = weather_map.get(code, "Unknown")
                
                return f"Weather in {city.title()}:\nTemperature: {temp}°C\nWind: {wind} km/h\nConditions: {description}"
            else:
                return f"Could not fetch weather for {city}"
                
    except APIError as e:
        return f"Error fetching weather: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# ─── Tool 2: News API ───

@tool
async def get_news(keyword: Optional[str] = None) -> str:
    """
    Get latest news headlines. Optionally search by keyword.
    
    Args:
        keyword: Optional keyword to search news
    
    Returns:
        str: News headlines
    """
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {"language": "en"}
            if keyword:
                params["keywords"] = keyword
            
            # Note: Free API may have rate limits
            # For demo, using mock data if API fails
            try:
                data = await call_api_with_retry(client, NEWS_API, params, max_retries=2)
                
                if "news" in data and data["news"]:
                    news_items = data["news"][:5]
                    result = f"Latest News{' about ' + keyword if keyword else ''}:\n\n"
                    for i, item in enumerate(news_items, 1):
                        title = item.get("title", "No title")
                        description = item.get("description", "")[:100]
                        result += f"{i}. {title}\n   {description}...\n\n"
                    return result
                else:
                    return "No news found"
                    
            except (APIError, httpx.HTTPStatusError):
                # Fallback to mock news
                return get_mock_news(keyword)
                
    except Exception as e:
        return f"Error fetching news: {str(e)}"

def get_mock_news(keyword: Optional[str] = None) -> str:
    """Mock news data as fallback"""
    
    mock_news = [
        {"title": "AI Breakthrough: New Model Achieves Human-Level Reasoning", "description": "Researchers at Stanford have developed a new AI model that can reason at human levels..."},
        {"title": "Global Climate Summit Reaches Historic Agreement", "description": "World leaders have agreed to reduce carbon emissions by 50% by 2035..."},
        {"title": "Pakistan's Economy Shows Strong Recovery", "description": "The Pakistani economy has shown remarkable recovery with GDP growth of 5.2%..."},
        {"title": "Tech Giants Invest $100B in AI Infrastructure", "description": "Major tech companies have announced a joint investment in AI infrastructure..."},
        {"title": "New Treatment for Cancer Shows Promise", "description": "A new immunotherapy treatment has shown promising results in clinical trials..."}
    ]
    
    if keyword:
        matched = [n for n in mock_news if keyword.lower() in n["title"].lower()]
        if matched:
            news_items = matched
        else:
            news_items = mock_news[:3]
    else:
        news_items = mock_news
    
    result = f"Latest News{' about ' + keyword if keyword else ''} (Mock Data):\n\n"
    for i, item in enumerate(news_items, 1):
        result += f"{i}. {item['title']}\n   {item['description']}\n\n"
    
    return result

# ─── Tool 3: Currency Converter ───

@tool
async def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert between currencies using real exchange rates.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency (USD, EUR, GBP, PKR, JPY, CAD)
        to_currency: Target currency (USD, EUR, GBP, PKR, JPY, CAD)
    
    Returns:
        str: Conversion result
    """
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            from_curr = from_currency.upper()
            to_curr = to_currency.upper()
            
            data = await call_api_with_retry(client, f"{CURRENCY_API}", max_retries=2)
            
            if "rates" in data:
                rates = data["rates"]
                
                if from_curr not in rates:
                    return f"Currency '{from_curr}' not supported"
                if to_curr not in rates:
                    return f"Currency '{to_curr}' not supported"
                
                # Convert
                if from_curr == "USD":
                    usd_amount = amount
                else:
                    usd_amount = amount / rates[from_curr]
                
                converted = usd_amount * rates[to_curr]
                
                return f"{amount:,.2f} {from_curr} = {converted:,.2f} {to_curr}\nRate: 1 {from_curr} = {rates[to_curr]/rates[from_curr]:.4f} {to_curr}"
            else:
                return "Could not fetch exchange rates"
                
    except APIError as e:
        return f"Error converting currency: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# ─── Tool 4: News Research Agent ───

class NewsResearchAgent:
    """Agent that searches news, extracts entities, classifies topics, and summarizes"""
    
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.history = []
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text using LLM"""
        
        prompt = ChatPromptTemplate.from_template("""
        Extract entities from the following text.
        Return as JSON with keys: people, organizations, locations, dates.
        
        Text: {text}
        
        JSON:
        """)
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({"text": text})
            return json.loads(result)
        except:
            return {"people": [], "organizations": [], "locations": [], "dates": []}
    
    def classify_topics(self, text: str) -> List[str]:
        """Classify topics from text using LLM"""
        
        prompt = ChatPromptTemplate.from_template("""
        Classify the following text into topics.
        Return only a list of topic labels.
        
        Text: {text}
        
        Topics:
        """)
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({"text": text})
            topics = [t.strip() for t in result.split('\\n') if t.strip()]
            return topics[:5]
        except:
            return ["General"]
    
    def summarize_findings(self, news_items: List[str], query: str) -> str:
        """Summarize news findings using LLM"""
        
        prompt = ChatPromptTemplate.from_template("""
        Summarize the following news articles related to: {query}
        
        News:
        {news}
        
        Provide a comprehensive summary covering:
        1. Key themes
        2. Important events
        3. Future implications
        
        Summary:
        """)
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            return chain.invoke({
                "query": query,
                "news": "\\n\\n".join(news_items)
            })
        except:
            return "Could not generate summary"

# ─── Error Recovery Agent ───

class ErrorRecoveryAgent:
    """Agent with error handling, retries, and fallback chains"""
    
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.tool_functions = {
            "weather": get_weather,
            "news": get_news,
            "currency": convert_currency
        }
        self.fallback_chain = {
            "weather": ["weather", "news"],
            "news": ["news", "weather"],
            "currency": ["currency", "news"]
        }
        self.logs = []
    
    def log_attempt(self, tool_name: str, attempt: int, result: str, success: bool):
        """Log attempt for tracking"""
        self.logs.append({
            "tool": tool_name,
            "attempt": attempt + 1,
            "result": result[:100] + "..." if len(result) > 100 else result,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_fallback_tools(self, tool_name: str) -> List[str]:
        """Get fallback tools for a given tool"""
        return self.fallback_chain.get(tool_name, [tool_name])
    
    async def execute_with_retry(
        self,
        tool_name: str,
        args: Dict,
        max_retries: int = 3,
        use_fallback: bool = True
    ) -> str:
        """Execute a tool with retries and fallbacks"""
        
        console.print(f"\\n[bold]Executing tool: {tool_name}[/bold]")
        
        # Primary tool execution with retries
        for attempt in range(max_retries):
            try:
                if tool_name in self.tool_functions:
                    result = await self.tool_functions[tool_name](**args)
                    self.log_attempt(tool_name, attempt, result, True)
                    console.print(f"[green]Success on attempt {attempt + 1}[/green]")
                    return result
                else:
                    return f"Tool '{tool_name}' not found"
                    
            except Exception as e:
                error_msg = f"Attempt {attempt + 1} failed: {str(e)}"
                self.log_attempt(tool_name, attempt, error_msg, False)
                console.print(f"[yellow]Warning: {error_msg}[/yellow]")
                
                if attempt < max_retries - 1:
                    delay = exponential_backoff(attempt)
                    console.print(f"[dim]Waiting {delay:.2f}s before retry...[/dim]")
                    await asyncio.sleep(delay)
        
        # If primary tool fails and fallback is enabled
        if use_fallback:
            fallbacks = self.get_fallback_tools(tool_name)
            for fallback in fallbacks[1:]:  # Skip the primary tool
                console.print(f"[dim]Trying fallback tool: {fallback}[/dim]")
                try:
                    if fallback in self.tool_functions:
                        result = await self.tool_functions[fallback](**args)
                        self.log_attempt(fallback, 0, result, True)
                        console.print(f"[green]Fallback successful: {fallback}[/green]")
                        return result
                except Exception as e:
                    console.print(f"[red]Fallback failed: {str(e)}[/red]")
        
        return f"All attempts failed for tool '{tool_name}'. Check logs for details."
    
    def show_logs(self):
        """Display execution logs"""
        
        console.print("\\n" + "="*70)
        console.print("[bold cyan]EXECUTION LOGS[/bold cyan]")
        console.print("="*70)
        
        if not self.logs:
            console.print("No logs available.")
            return
        
        table = Table(title="Tool Execution Logs", box=box.ROUNDED)
        table.add_column("#", style="dim", width=3)
        table.add_column("Tool", style="cyan")
        table.add_column("Attempt", style="yellow", justify="center")
        table.add_column("Status", style="green")
        table.add_column("Result", style="white")
        
        for i, log in enumerate(self.logs, 1):
            status = "Success" if log["success"] else "Failed"
            table.add_row(
                str(i),
                log["tool"],
                str(log["attempt"]),
                status,
                log["result"][:50] + "..." if len(log["result"]) > 50 else log["result"]
            )
        
        console.print(table)

# ─── Main Demo ───

async def main():
    """Main entry point"""
    
    console.print(Panel.fit(
        "[bold white]Week 2 - Day 4: External APIs as Tools[/bold white]\\n"
        "[cyan]Lab 2.3 - Error Recovery Agent with Real APIs[/cyan]",
        border_style="cyan"
    ))
    
    # Test tools
    console.print("\\n[bold cyan]Testing External API Tools...[/bold cyan]\\n")
    
    # Weather test
    console.print("[bold]1. Weather API Test[/bold]")
    weather_result = await get_weather("London")
    console.print(weather_result)
    console.print("")
    
    # News test
    console.print("[bold]2. News API Test[/bold]")
    news_result = await get_news()
    console.print(news_result)
    console.print("")
    
    # Currency test
    console.print("[bold]3. Currency API Test[/bold]")
    currency_result = await convert_currency(100, "USD", "PKR")
    console.print(currency_result)
    console.print("")
    
    # Error Recovery Agent
    console.print("[bold cyan]4. Error Recovery Agent Demo[/bold cyan]")
    console.print("Testing error handling with retries and fallbacks...\\n")
    
    agent = ErrorRecoveryAgent()
    
    # Test with a tool that might fail
    result = await agent.execute_with_retry(
        "weather",
        {"city": "London"},
        max_retries=3
    )
    console.print(f"\\n[bold]Final Result:[/bold]\\n{result}")
    
    agent.show_logs()
    
    # News Research Agent Demo
    console.print("\\n[bold cyan]5. News Research Agent Demo[/bold cyan]")
    
    research_agent = NewsResearchAgent()
    
    # Get news
    news_result = await get_news("AI")
    console.print("[bold]News Headlines:[/bold]")
    console.print(news_result)
    
    # Extract entities
    console.print("\\n[bold]Entity Extraction:[/bold]")
    entities = research_agent.extract_entities(news_result)
    console.print(json.dumps(entities, indent=2))
    
    # Classify topics
    console.print("\\n[bold]Topic Classification:[/bold]")
    topics = research_agent.classify_topics(news_result)
    console.print(topics)

if __name__ == "__main__":
    asyncio.run(main())
