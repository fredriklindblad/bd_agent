# Agents Module

This package contains the modular AI agents that make up the **BD Agent** system.  
Each agent is designed to handle a specific part of the investment analysis workflow — from interpreting user intent to screening, analyzing, and advising on stocks.

---

## Overview

| Agent | Description |
|-------|--------------|
MAIN AGENTS
| `screener_agent` | Filters and ranks companies based on user-defined criteria using Börsdata data. |
| `analyze_agent` | Performs deeper company-level analysis (valuation, profitability, growth). |
| `advisor_agent` | Provides personalized investment advice and insights using aggregated agent outputs. |
| `portfolio_agent` | Analyzes user portfolios, performance, diversification, and risk metrics. |

SUPPORT AGENTS
| `_name_interpretation_agent` | Identifies and normalizes company names, tickers, and symbols in user prompts. |
| `_find_industry_kpis` | Maps industries to their relevant financial KPIs and benchmarks. |
---
