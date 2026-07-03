# Project 2-P-C: Financial Data Analysis Agent — Run Guide

**File:** `week2/project2_p_c_financial_analysis.py`  
**Type:** Streamlit Web App — runs in browser  
**Category:** Production  

---

## What This Project Does

A professional Streamlit web application that accepts any financial CSV and lets you ask natural-language questions. The agent:

1. Profiles your dataset (schema, types, nulls, stats)
2. Routes your question to the right analysis tool
3. Generates Python/pandas/plotly code via Groq LLM
4. Executes the code safely in a subprocess sandbox
5. Renders interactive Plotly charts
6. Produces a professional narrative report
7. Lets you download the report, code, and structured JSON result

---

## How to Run — One Command

### Step 1 — Activate environment

```powershell
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\Activate.ps1
```

### Step 2 — Launch the app

```powershell
python -m streamlit run week2/project2_p_c_financial_analysis.py
```

The browser opens automatically at `http://localhost:8501`.

---

## Sample CSV Files — Copy and Paste to Create

### Sample 1: Stock Prices (recommended for first test)

Create a file called `stocks.csv` and paste this content:

```
Date,Open,High,Low,Close,Volume,Symbol
2026-01-02,150.25,155.40,149.80,154.30,2500000,AAPL
2026-01-03,154.30,157.20,153.10,156.80,2800000,AAPL
2026-01-06,156.80,160.50,155.90,159.40,3100000,AAPL
2026-01-07,159.40,162.30,158.20,161.70,2900000,AAPL
2026-01-08,161.70,165.00,160.80,164.50,3400000,AAPL
2026-01-09,164.50,166.20,162.10,163.20,2600000,AAPL
2026-01-12,163.20,167.80,162.50,167.10,3200000,AAPL
2026-01-13,167.10,170.40,166.30,169.80,3600000,AAPL
2026-01-14,169.80,172.50,168.90,171.20,3100000,AAPL
2026-01-15,171.20,174.00,170.10,173.60,2800000,AAPL
2026-01-16,173.60,175.30,172.20,174.90,2500000,AAPL
2026-01-20,174.90,178.10,174.20,177.50,3300000,AAPL
2026-01-21,177.50,180.30,176.80,179.20,3700000,AAPL
2026-01-22,179.20,181.50,177.90,180.80,3000000,AAPL
2026-01-23,180.80,183.20,179.50,182.40,2900000,AAPL
2026-02-03,182.40,185.10,181.20,184.70,3100000,AAPL
2026-02-04,184.70,187.30,183.80,186.20,3400000,AAPL
2026-02-05,186.20,188.90,185.40,188.50,3200000,AAPL
2026-02-06,188.50,191.20,187.30,190.10,3500000,AAPL
2026-02-09,190.10,192.80,189.20,192.40,3000000,AAPL
```

---

### Sample 2: Portfolio Returns

Create `portfolio.csv` and paste this:

```
Month,Equities,Bonds,Cash,Gold,Total_Return
Jan-2026,8.50,2.10,0.40,3.20,4.80
Feb-2026,-3.20,1.80,0.40,-1.50,-0.90
Mar-2026,5.60,0.90,0.40,2.10,3.40
Apr-2026,2.30,1.20,0.40,4.50,2.70
May-2026,-1.80,2.50,0.40,-0.80,0.40
Jun-2026,7.20,0.60,0.40,1.80,4.20
Jul-2026,4.10,1.40,0.40,5.20,3.60
Aug-2026,-2.50,3.10,0.40,2.40,0.90
Sep-2026,6.80,0.80,0.40,-1.20,3.50
Oct-2026,3.40,1.60,0.40,3.80,2.80
Nov-2026,9.20,0.40,0.40,0.90,5.10
Dec-2026,1.50,2.20,0.40,6.30,3.10
```

---

### Sample 3: Transaction Ledger

Create `transactions.csv` and paste this:

```
Date,Category,Amount,Currency,Status,Merchant
2026-01-05,Salary,5000.00,USD,Completed,Employer Inc
2026-01-08,Rent,-1500.00,USD,Completed,Property Co
2026-01-10,Groceries,-120.50,USD,Completed,FreshMart
2026-01-12,Utilities,-85.30,USD,Completed,CityPower
2026-01-15,Investment,-500.00,USD,Completed,Vanguard
2026-01-18,Dining,-65.00,USD,Completed,RestaurantXYZ
2026-01-20,Transport,-45.20,USD,Completed,Uber
2026-01-25,Freelance,800.00,USD,Completed,Client A
2026-02-05,Salary,5000.00,USD,Completed,Employer Inc
2026-02-08,Rent,-1500.00,USD,Completed,Property Co
2026-02-10,Groceries,-135.20,USD,Completed,FreshMart
2026-02-12,Utilities,-92.10,USD,Completed,CityPower
2026-02-14,Investment,-500.00,USD,Completed,Vanguard
2026-02-20,Dining,-78.50,USD,Completed,RestaurantXYZ
2026-02-22,Transport,-52.80,USD,Completed,Uber
2026-02-28,Freelance,1200.00,USD,Completed,Client B
2026-03-05,Salary,5000.00,USD,Completed,Employer Inc
2026-03-08,Rent,-1500.00,USD,Completed,Property Co
2026-03-15,Investment,-750.00,USD,Pending,Vanguard
2026-03-18,Groceries,-98.70,USD,Completed,FreshMart
```

---

## Test Questions — Copy and Paste into the App

### For `stocks.csv`

| Question | Expected Result |
|---|---|
| `What is the average closing price?` | Numeric value around 172-175 |
| `Plot the closing price over time as a line chart` | Line chart showing upward trend |
| `What is the highest closing price and on which date?` | 192.40 on 2026-02-09 |
| `Show the distribution of daily volume as a histogram` | Histogram of volume column |
| `Calculate the percentage change from first to last close` | Around 25-28% gain |
| `What is the correlation between volume and closing price?` | Correlation coefficient value |

### For `portfolio.csv`

| Question | Expected Result |
|---|---|
| `Which asset class had the highest average return?` | Likely Equities or Gold |
| `Plot all asset returns over the months as a line chart` | Multi-line chart with 4 series |
| `What month had the best total return?` | November 2026 (5.10%) |
| `Show a bar chart of total returns by month` | Bar chart with 12 months |
| `Calculate the average total return across all months` | Around 2.8-3.1% |
| `Which months had negative total returns?` | Feb and May 2026 |

### For `transactions.csv`

| Question | Expected Result |
|---|---|
| `What is the total amount spent on Groceries?` | Around -354.40 |
| `Show a bar chart of spending by category` | Bar chart of categories |
| `What is my net savings each month?` | Monthly totals (Salary - Expenses) |
| `Which category has the most transactions?` | One of the recurring categories |
| `What percentage of transactions are completed vs pending?` | 95% completed, 5% pending |
| `Plot the cumulative balance over time` | Running total line chart |

---

## Step-by-Step Test Procedure

1. **Start the app:**
   ```powershell
   python -m streamlit run week2/project2_p_c_financial_analysis.py
   ```

2. **Browser opens** at `http://localhost:8501` — you should see the dark interface.

3. **Click "Browse files"** or drag-and-drop one of the CSV files above.

4. **Wait 2-3 seconds** — the sidebar will show live USD exchange rates and the main area will show:
   - 4 metric cards (Rows, Columns, Null Cells, Numeric Columns)
   - Preview tab with first 20 rows
   - Schema tab with column types
   - Statistics tab with describe() output

5. **Type a question** from the test cases above into the text box.

6. **Click "Run Analysis"** — watch the tool selection badge appear, then:
   - The generated Python code is shown in a code block
   - The chart or text output appears
   - A professional narrative report is generated below

7. **Download** using the three buttons at the bottom:
   - **Download Report (Markdown)** — professional .md file
   - **Download Analysis Code** — the exact Python that ran
   - **Download Structured Result (JSON)** — Pydantic AnalysisResult

---

## UI Walkthrough

```
┌─────────────────────────────────────────────────────────────────┐
│ SIDEBAR                          │ MAIN AREA                    │
│                                  │                              │
│ Live Rates                       │ Financial Data Analysis      │
│ 1 USD = 0.9200 EUR               │ Agent                        │
│ 1 USD = 0.7900 GBP               │                              │
│ 1 USD = 279.50 PKR               │ [Step 1] Upload Data         │
│ ...                              │ ┌──────────────────────┐     │
│                                  │ │  Drop CSV here       │     │
│ About                            │ └──────────────────────┘     │
│ Week 2, Day 5                    │                              │
│ CalderR AI Internship            │ [After upload]               │
│                                  │ Rows: 20  Cols: 6            │
│ Week 2 Learning                  │ Nulls: 0  Numeric: 5         │
│ Day 1: CoT prompting             │                              │
│ Day 2: Pydantic output           │ [Preview] [Schema] [Stats]   │
│ Day 3: Tool agent pattern        │                              │
│ Day 4: API + retry logic         │ [Step 2] Ask a Question      │
│ Day 5: Integration               │ [text box]                   │
│                                  │ [Run Analysis] Tool: plot    │
│                                  │                              │
│                                  │ Generated Code               │
│                                  │ [code block]                 │
│                                  │                              │
│                                  │ [Interactive Plotly Chart]   │
│                                  │                              │
│                                  │ Analysis Report              │
│                                  │ ## Executive Summary...      │
│                                  │                              │
│                                  │ [Download MD][Download PY]   │
│                                  │ [Download JSON]              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Features Demonstrated

| Feature | Week 2 Day | Description |
|---|---|---|
| Pydantic `AnalysisResult` | Day 2 | Every analysis is a typed, validated schema |
| `ColumnSchema` profiling | Day 2 | Dataset schema extracted into Pydantic models |
| Five analysis tools | Day 3 | `describe`, `plot`, `correlate`, `filter`, `stats` |
| Tool routing by keyword | Day 3 | Selects tool from question without LLM overhead |
| CoT code generation | Day 1 | LLM reasons step-by-step before writing code |
| CoT report generation | Day 1 | Same CoT pattern for narrative report |
| Live currency rates | Day 4 | External API fetch with exponential backoff |
| Subprocess sandboxing | Day 4 | Code runs in isolated process, 30s timeout |
| Session history | Day 5 | All analyses tracked in `st.session_state` |
| Dark professional UI | Day 5 | Navy + blue accent, metric cards, tabs |

---

## Troubleshooting

| Error | Fix |
|---|---|
| `GROQ_API_KEY not set` | Add `GROQ_API_KEY=your_key` to `.env` file |
| `ModuleNotFoundError: plotly` | Run `pip install plotly` |
| `ModuleNotFoundError: streamlit` | Run `pip install streamlit` |
| Chart not showing | The LLM may not have used `fig` variable — try rephrasing as "plot a chart of..." |
| App shows blank | Refresh the browser at `http://localhost:8501` |
| Execution timed out | The analysis was too complex — simplify the question |
| `use_container_width` warning | Harmless deprecation warning from Streamlit, does not affect functionality |
