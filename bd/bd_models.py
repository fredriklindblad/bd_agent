from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Iterable

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
    
class AnalyzeRequest(BaseModel):
    company: str = Field(..., description="Ticker eller bolagsnamn extraherat ur prompten")

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

