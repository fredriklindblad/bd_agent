# screener_agent/models.py

from pydantic import BaseModel
from typing import Optional, List


class ScreenerFilterRequest(BaseModel):
    """
    Denna modell används som input till screener-agenten.
    Den speglar användarens naturliga språkfråga, t.ex.:
    'Visa investmentbolag i Sverige' → {"branch": "Investmentbolag", "country": "Sverige"}
    """
    country: Optional[str] = None
    sector: Optional[str] = None
    market: Optional[str] = None
    branch: Optional[str] = None
    instrument_type: Optional[str] = None


class ScreenerStockResult(BaseModel):
    """
    Enskilt bolag i resultatlistan från screenern.
    """
    ticker: str
    name: str
    country: Optional[str] = None
    sector: Optional[str] = None
    branch: Optional[str] = None


class ScreenerResponse(BaseModel):
    """
    Responsemodell för screener-agenten, med lista av matchade bolag.
    """
    # results: List[ScreenerStockResult]
    results: List[ScreenerStockResult]
