from pydantic import BaseModel
from typing import Optional


class Instrument(BaseModel):
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
