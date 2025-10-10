"""Models for the BD fetched data is created here"""

from pydantic import BaseModel
from typing import Optional


class InstrumentInfo(BaseModel):
    insId: int
    name: str
    insType: Optional[int] = None
    isin: Optional[str] = None
    ticker: Optional[str] = None
    sectorId: Optional[int] = None
    marketId: Optional[int] = None
    branchId: Optional[int] = None
    countryId: Optional[int] = None
    stockPriceCurrency: Optional[str] = None
    reportCurrency: Optional[str] = None
