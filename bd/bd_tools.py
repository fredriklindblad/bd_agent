# bd/bd_tools.py
# Hämtar universumet av instrument

from typing import List, Optional

import requests
from bd_models import Instrument

from config import get_bdapi_key

BASE_URL = "https://apiservice.borsdata.se/v1"


# ------------------------
# Instruments
# ------------------------
def get_nordics_instruments() -> List[Instrument]:
    url = f"{BASE_URL}/instruments?authKey={get_bdapi_key()}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()

    print(data)

    nordics_instruments = []
    for item in data["instruments"]:
        nordics_instruments.append(
            Instrument(
                id=item["insId"],
                name=item["name"],
                ticker=item["ticker"],
                instrument_type=item.get("instrument"),
                isin=item.get("isin"),
                sector_id=item.get("sectorId"),
                country_id=item.get("countryId"),
                market_id=item.get("marketId"),
                branch_id=item.get("branchId"),
                stock_price_currency=item.get("stockPriceCurrency"),
                report_currency=item.get("reportCurrency"),
            )
        )
    return nordics_instruments


def get_global_instruments() -> List[Instrument]:
    url = f"{BASE_URL}/instruments/global?authKey={get_bdapi_key()}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()

    global_instruments = []
    for item in data["instruments"]:
        global_instruments.append(
            Instrument(
                id=item["insId"],
                name=item["name"],
                ticker=item["ticker"],
                instrument_type=item.get("instrument"),
                isin=item.get("isin"),
                sector_id=item.get("sectorId"),
                country_id=item.get("countryId"),
                market_id=item.get("marketId"),
                branch_id=item.get("branchId"),
                stock_price_currency=item.get("stockPriceCurrency"),
                report_currency=item.get("reportCurrency"),
            )
        )
    return global_instruments


def _instrument_id_by_ticker(ticker: str) -> Optional[int]:
    t = (ticker or "").upper()
    for inst in get_global_instruments():
        if inst.ticker and inst.ticker.upper() == t:
            return inst.id
    return None
