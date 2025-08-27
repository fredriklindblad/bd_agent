from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Instrument(BaseModel):
    id: int
    name: str
    ticker: str
    instrument_type: Optional[int]
    isin: Optional[str]
    sector_id: Optional[int]
    country_id: Optional[int]
    market_id: Optional[int]
    branch_id: Optional[int]
    stock_price_currency: Optional[str]
    report_currency: Optional[str]


class ToolCall(BaseModel):
    name: str = Field(
        ..., description="Vilket tool som anropades, t.ex. 'resolve_ticker_tool'"
    )
    arguments: Dict[str, Any] = Field(
        default_factory=dict, description="Argument som skickades till tool:et"
    )
    output_preview: Optional[str] = Field(
        default=None,
        description="Kort sammanfattning av tool-output (för logg/insyn, ej för analyslogik)",
    )
    timestamp_utc: Optional[str] = Field(
        default=None,
        description="ISO8601 UTC-tid när anropet gjordes (om du vill tidsstämpla)",
    )


class AnalyzeRequest(BaseModel):
    company: str = Field(
        ..., description="Ticker eller bolagsnamn extraherat ur prompten"
    )
    rationale: Optional[str] = Field(
        default=None,
        description="Kort motivering från LLM kring varför detta bolag/ticker valdes",
    )
    tools_used: List[str] = Field(
        default_factory=list,
        description="Lista av tool-namn som användes (fylls i av koden efter körning)",
    )
    deps_used: List[str] = Field(
        default_factory=list,
        description="Lista av dependency-namn som användes (fylls i av koden efter körning)",
    )
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="Detaljerade tool-anrop (namn, args, output-preview, ev. timestamp)",
    )


class Metrics(BaseModel):
    as_of: Optional[str] = None
    year: int
    price: Optional[float] = None
    market_cap: Optional[float] = None
    pe: Optional[float] = None
    ev_ebit: Optional[float] = None
    ev_sales: Optional[float] = None
    roic: Optional[float] = None
    ebit_margin: Optional[float] = None
    gross_margin: Optional[float] = None
    revenue_cagr_5y: Optional[float] = None
    ebit_cagr_5y: Optional[float] = None
    net_debt_ebitda: Optional[float] = None
    interest_coverage: Optional[float] = None
    payout_ratio: Optional[float] = None
    dividend_stability_years: Optional[int] = None
    rule_of_40: Optional[float] = None


class ScoreItem(BaseModel):
    metric: str
    value: Optional[float] = None
    rule: Optional[str] = None
    passed: Optional[bool] = None


class Scorecard(BaseModel):
    valuation: List[ScoreItem] = []
    quality: List[ScoreItem] = []
    growth: List[ScoreItem] = []
    health: List[ScoreItem] = []
    dividend: List[ScoreItem] = []
    signals: List[ScoreItem] = []
    overall_pass: Optional[bool] = None


class AnalyzeResponse(BaseModel):
    ticker: str
    name: str
    market: Optional[str] = None
    sector: Optional[str] = None
    branch: Optional[str] = None

    snapshot: Metrics
    scorecard: Scorecard

    verdict: str
    thesis: str
    risks: List[str] = []
    catalysts: List[str] = []
