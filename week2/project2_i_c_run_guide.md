# Project 2-I-C: API Aggregator Agent — Run Guide

**File:** `week2/project2_i_c_api_aggregator.py`  
**Type:** CLI (Command Line) — runs in terminal  
**Category:** Intermediate  

---

## What This Project Does

Fetches data from **3 public APIs simultaneously** (parallel async calls) and synthesises a professional financial morning briefing report using an LLM.

**Pipeline:**
```
asyncio.gather (3 parallel API calls)
    -> Open-Meteo        (weather for your city)
    -> exchangerate-api  (USD exchange rates)
    -> GNews / mock data (financial news headlines)
DataAggregator -> BriefingReport (Pydantic schema)
    -> Groq LLM (chain-of-thought synthesis)
    -> report_TIMESTAMP.md  (saved to disk)
    -> report_TIMESTAMP.html (saved to disk)
```

---

## How to Run

### Step 1 — Activate environment

```powershell
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\Activate.ps1
```

### Step 2 — Run the script

```powershell
python week2/project2_i_c_api_aggregator.py
```

### Step 3 — Enter a city when prompted

```
Enter city for weather (default: London):
```

Type one of the supported cities and press Enter (or just press Enter for London):

```
london | paris | new york | tokyo | dubai
karachi | islamabad | lahore | mumbai | singapore
```

---

## What You Will See

```
API Aggregator Agent
Week 2 - Day 5 | Project 2-I-C
Financial Morning Briefing

Aggregating data for London...

API Data Summary
┌────────────────┬────────┬─────────────────────────────────────┐
│ Source         │ Status │ Detail                              │
├────────────────┼────────┼─────────────────────────────────────┤
│ Weather        │ OK     │ London: 18.5C, Partly Cloudy        │
│ Financial News │ OK     │ 5 headlines fetched                 │
│ Currency       │ OK     │ 10 pairs loaded                     │
└────────────────┴────────┴─────────────────────────────────────┘

Synthesising morning briefing report (chain-of-thought LLM)...

Morning Briefing Report
┌─────────────────────────────────────────────────────────────┐
│ ## Executive Summary                                        │
│ Global equity markets are showing signs of recovery...      │
│                                                             │
│ ## Weather & Operational Context                            │
│ London: 18.5°C, Partly Cloudy, winds at 14 km/h...         │
│                                                             │
│ ## Financial Markets Update                                 │
│ - Global Equities Advance as Inflation Data Eases...        │
│                                                             │
│ ## Currency Snapshot                                        │
│ 1 USD = 0.9200 EUR | 0.7900 GBP | 279.5000 PKR...         │
│                                                             │
│ ## Key Takeaways & Outlook                                  │
│ - Risk-on sentiment is returning to markets...              │
└─────────────────────────────────────────────────────────────┘

Reports saved:
  report_20260703_154500.md
  report_20260703_154500.html

Structured Data (Pydantic JSON):
{
  "city": "London",
  "timestamp": "2026-07-03T15:45:00",
  "weather": { "city": "London", "temperature": 18.5, ... }
  ...
}
```

---

## Output Files

After running, two report files are saved in the project root:

| File | Format | Contents |
|---|---|---|
| `report_TIMESTAMP.md` | Markdown | Full briefing report with header |
| `report_TIMESTAMP.html` | HTML | Dark-themed styled report, open in browser |

**View the HTML report:**
```powershell
start report_20260703_154500.html
```

---

## Test Cases — Copy and Paste

### Test Case 1 — London (default)
```
Enter city for weather (default: London): [press Enter]
```
Expected: Weather data for London (51.5°N), 5 financial news headlines, 10 currency pairs.

### Test Case 2 — Karachi
```
Enter city for weather (default: London): karachi
```
Expected: Weather data for Karachi (24.8°N), same news/currency data since those are global.

### Test Case 3 — Dubai
```
Enter city for weather (default: London): dubai
```
Expected: Weather data for Dubai (25.2°N), typically hot and clear.

### Test Case 4 — Tokyo
```
Enter city for weather (default: London): tokyo
```
Expected: Weather data for Tokyo (35.7°N).

### Test Case 5 — Invalid city
```
Enter city for weather (default: London): berlin
```
Expected: `Weather unavailable: City 'berlin' not in coordinate map.` — the agent continues and generates the report using news + currency data only.

---

## Features Demonstrated

| Feature | Week 2 Day | Description |
|---|---|---|
| Parallel async API calls | Day 3 + 4 | `asyncio.gather` runs all 3 fetches simultaneously |
| Exponential backoff | Day 4 | Every API call retries with `min(base*2^n, cap) + jitter` |
| Pydantic structured output | Day 2 | `BriefingReport`, `WeatherData`, `CurrencyData` schemas |
| Chain-of-thought prompt | Day 1 | LLM reasons in 4 steps before writing the report |
| Fallback to mock data | Day 4 | News falls back to curated mock if API unavailable |
| Tool routing pattern | Day 3 | Three separate async tool functions, dispatched by aggregator |
| Rich terminal output | All | Tables, panels, color-coded status |
| HTML + Markdown export | Day 5 | Two report formats saved automatically |

---

## Troubleshooting

| Error | Fix |
|---|---|
| `GROQ_API_KEY not set` | Add `GROQ_API_KEY=your_key` to `.env` file |
| `ModuleNotFoundError: httpx` | Run `pip install httpx` |
| `City not found` | Use a city from the supported list above |
| Report generation fails | Check internet connection; the LLM call requires Groq API access |
