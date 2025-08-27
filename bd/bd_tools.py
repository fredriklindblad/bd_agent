# bd/bd_tools.py
# Hämtar universumet av instrument

from typing import Any, Dict, List, Optional

import requests

from bd.bd_models import Instrument
from bd.config import get_bdapi_key

BASE_URL = "https://apiservice.borsdata.se/v1"


# ------------------------
# Instruments
# ------------------------
def get_nordics_instruments() -> List[Instrument]:
    url = f"{BASE_URL}/instruments?authKey={get_bdapi_key()}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()

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


# ------------------------
# Helpers
# ------------------------
def _first_non_none(*vals):
    for v in vals:
        if v is not None:
            return v
    return None


def _get(url: str) -> Optional[Dict[str, Any]]:
    try:
        r = requests.get(url, timeout=15)
        if r.ok:
            return r.json()
        return None
    except Exception:
        return None


def _g(d: Dict[str, Any], *names):
    for n in names:
        if isinstance(d, dict) and n in d:
            return d[n]
    return None


def _instrument_id_by_ticker(ticker: str) -> Optional[int]:
    t = (ticker or "").upper()
    for inst in get_global_instruments():
        if inst.ticker and inst.ticker.upper() == t:
            return inst.id
    return None


def _kpi_history_latest(
    ins_id: int, kpi_id: int, report: str, price: str
) -> Optional[Dict[str, Any]]:
    """
    Hämtar KPI-historik och returnerar senaste datapunkten.
    URL-format: /v1/instruments/{insId}/kpis/{kpiId}/{report}/{price}/history
    report ∈ {"year","r12","quarter"}, price ∈ {"mean","low","high"}
    """
    ak = get_bdapi_key()
    url = f"{BASE_URL}/instruments/{ins_id}/kpis/{kpi_id}/{report}/{price}/history?authKey={ak}"
    data = _get(url)
    if not data:
        return None
    values = data.get("values") or []
    if not isinstance(values, list) or not values:
        return None
    # sortera på (år, period) och ta sista
    try:
        values.sort(key=lambda x: (x.get("y", 0), x.get("p", 0)))
    except Exception:
        pass
    last = values[-1]
    return {"value": last.get("v"), "year": last.get("y"), "period": last.get("p")}


# ------------------------
# KPI metadata (för att slå upp KPI-id via namn)
# ------------------------
_KPI_META_CACHE: Optional[List[Dict[str, Any]]] = None


def _load_kpi_meta() -> List[Dict[str, Any]]:
    global _KPI_META_CACHE
    if _KPI_META_CACHE is not None:
        return _KPI_META_CACHE
    url = f"{BASE_URL}/kpis?authKey={get_bdapi_key()}"
    data = _get(url) or {}
    items = data.get("kpis") or data.get("items") or []
    _KPI_META_CACHE = items if isinstance(items, list) else []
    return _KPI_META_CACHE


def _kpi_id_by_names(*candidates: str) -> Optional[int]:
    """
    Försök hitta KPI-id genom att matcha mot name/engName/calcName (case-insensitive, contains).
    """
    meta = _load_kpi_meta()
    if not meta:
        return None
    cand_norm = [c.lower() for c in candidates if c]
    best: Optional[int] = None
    for row in meta:
        name_fields = [
            str(row.get("name", "")),
            str(row.get("engName", "")),
            str(row.get("calcName", "")),
            str(row.get("shortName", "")),
        ]
        joined = " ".join(name_fields).lower()
        if any(c in joined for c in cand_norm):
            best = row.get("kpiId") or row.get("id")
            if best is not None:
                return int(best)
    return None


def _kpi_value_latest_by_names(
    ins_id: int, names: List[str], report_order=("r12", "year")
) -> Optional[float]:
    kpi_id = _kpi_id_by_names(*names)
    if kpi_id is None:
        return None
    for rep in report_order:
        hit = _kpi_history_latest(ins_id, kpi_id, rep, "mean")
        if hit and hit.get("value") is not None:
            return float(hit["value"])
    return None


# ------------------------
# Key ratios (via KPI History)
# ------------------------
# kpiId enligt kända ID för några centrala KPI:er
KPI = {
    "PE": 2,
    "EV_EBIT": 10,
    "EV_Sales": 15,
    "ROIC": 37,
    "GrossMargin": 28,  # Bruttomarginal
    "EbitMargin": 29,  # Rörelsemarginal
    "NetDebtEbitda": 42,  # Nettoskuld/EBITDA
    # Interest coverage, Payout ratio, Dividend stability hämtas via _kpi_id_by_names()
}


def get_key_ratios_latest_by_id(ins_id: int) -> Dict[str, Any]:
    """
    Returnerar ett dict med senaste värden för de KPI:er som Analyze-agenten förväntar sig.
    Vi provar r12/mean först och faller tillbaka till year/mean om r12 saknas.
    """
    out: Dict[str, Any] = {}

    def grab_fixed(key: str, report_order=("r12", "year")):
        kpi_id = KPI[key]
        val = None
        year = None
        for rep in report_order:
            hit = _kpi_history_latest(ins_id, kpi_id, rep, "mean")
            if hit and hit.get("value") is not None:
                val = hit["value"]
                year = hit.get("year")
                break
        return val, year

    # Fasta KPI-id
    pe, y1 = grab_fixed("PE")
    ev_ebit, y2 = grab_fixed("EV_EBIT")
    ev_sales, y3 = grab_fixed("EV_Sales")
    roic, y4 = grab_fixed("ROIC")
    gross, y5 = grab_fixed("GrossMargin", report_order=("r12", "year"))
    ebitm, y6 = grab_fixed("EbitMargin", report_order=("r12", "year"))
    nd_ebitda, y7 = grab_fixed("NetDebtEbitda")

    out.update(
        {
            "PE": pe,
            "EV_EBIT": ev_ebit,
            "EV_Sales": ev_sales,
            "ROIC": roic,
            "GrossMargin": gross,
            "EbitMargin": ebitm,
            "NetDebtEbitda": nd_ebitda,
        }
    )

    # Dynamiska KPI-id via namn (Health + Dividend)
    # Interest coverage
    interest_cov = _kpi_value_latest_by_names(
        ins_id,
        ["Interest Coverage", "InterestCoverage", "Ränte", "Räntetäckningsgrad"],
        report_order=("year", "r12"),
    )
    if interest_cov is not None:
        out["InterestCoverage"] = interest_cov

    # Payout ratio
    payout_ratio = _kpi_value_latest_by_names(
        ins_id,
        ["Payout Ratio", "PayoutRatio", "Utdelningsandel"],
        report_order=("year", "r12"),
    )
    if payout_ratio is not None:
        out["PayoutRatio"] = payout_ratio

    # Dividend stability years
    div_stab = _kpi_value_latest_by_names(
        ins_id,
        ["Dividend Stability Years", "DividendStabilityYears", "Utdelningsstabilitet"],
        report_order=("year", "r12"),
    )
    if div_stab is not None:
        # vissa KPI kan komma i år, men ofta finns inte—om finns, exponera som årtal/antal
        out["DividendStabilityYears"] = div_stab

    # "asOf" – välj första befintliga årtalet
    out["asOf"] = _first_non_none(y1, y2, y3, y4, y5, y6, y7)

    # rensa None:or
    return {k: v for k, v in out.items() if v is not None}


def get_key_ratios_latest_by_ticker(ticker: str) -> Dict[str, Any]:
    t = (ticker or "").upper()
    ins_id = next(
        (i.id for i in get_global_instruments() if (i.ticker or "").upper() == t), None
    )
    if ins_id is None:
        return {}
    return get_key_ratios_latest_by_id(ins_id)


# ------------------------
# Last quote / price
# ------------------------
def get_quote_by_id(ins_id: int) -> Dict[str, Any]:
    """
    /v1/instruments/stockprices/last returnerar ALLA instrument i en lista "stockPricesList".
    Vi filtrerar fram rätt instrument och mappar fält till {price, marketCap, asOf}.
    Obs: marketCap följer normalt inte med här – lämnas som None.
    """
    ak = get_bdapi_key()
    url = f"{BASE_URL}/instruments/stockprices/last?authKey={ak}"
    data = _get(url) or {}
    items = data.get("stockPricesList") or []
    row = next(
        (
            x
            for x in items
            if (
                x.get("i") == ins_id
                or x.get("insId") == ins_id
                or x.get("instrumentId") == ins_id
            )
        ),
        None,
    )
    if not row:
        return {}
    price = _first_non_none(
        row.get("price"), row.get("c"), row.get("last"), row.get("close")
    )
    as_of = row.get("d") or row.get("date")
    return {"price": price, "marketCap": None, "asOf": as_of}


def get_quote_by_ticker(ticker: str) -> Dict[str, Any]:
    t = (ticker or "").upper()
    ins_id = next(
        (i.id for i in get_global_instruments() if (i.ticker or "").upper() == t), None
    )
    if ins_id is None:
        return {}
    return get_quote_by_id(ins_id)


# ------------------------
# Extra KPI-historik för CAGR och liknande
# ------------------------
def _kpi_history_by_id(
    ins_id: int, kpi_id: int, reporttype: str = "year", pricetype: str = "mean"
) -> List[Dict[str, Any]]:
    """Returnerar lista [{'year': 2024, 'value': 123.4}, ...] för given KPI."""
    url = f"{BASE_URL}/instruments/{ins_id}/kpis/{kpi_id}/{reporttype}/{pricetype}/history?authKey={get_bdapi_key()}"
    data = _get(url) or {}

    values = data.get("values") or data.get("items") or data.get("data") or []
    out = []
    for row in values:
        if isinstance(row, dict):
            y = row.get("y") or row.get("year")
            v = row.get("v") or row.get("value")
            if y is not None and v is not None:
                try:
                    out.append({"year": int(y), "value": float(v)})
                except Exception:
                    continue
    # Sortera (senaste först)
    out.sort(key=lambda x: x["year"], reverse=True)
    return out


def _latest_kpi_value(
    ins_id: int, kpi_id: int, reporttype: str = "year"
) -> Optional[float]:
    # pröva year först, annars r12
    for rep in (reporttype, "r12"):
        hist = _kpi_history_by_id(ins_id, kpi_id, rep, "mean")
        if hist:
            return hist[0]["value"]
    return None


def _cagr(values: List[Dict[str, Any]], years: int = 5) -> Optional[float]:
    """CAGR i % från year-(years) till year (senaste först i values)."""
    if len(values) < years + 1:
        return None
    last = values[0]["value"]
    first = values[years]["value"]
    if first <= 0 or last <= 0:
        return None
    cagr = (last / first) ** (1 / years) - 1
    return 100.0 * cagr


# Publika wrappers du kan kalla från analyze_agent:
def get_roic_latest(ins_id: int) -> Optional[float]:  # KpiId 37
    return _latest_kpi_value(ins_id, 37)


def get_gross_margin_latest(ins_id: int) -> Optional[float]:  # KpiId 28
    return _latest_kpi_value(ins_id, 28)


def get_ebit_margin_latest(ins_id: int) -> Optional[float]:  # KpiId 29
    return _latest_kpi_value(ins_id, 29)


def get_netdebt_ebitda_latest(ins_id: int) -> Optional[float]:  # KpiId 42
    return _latest_kpi_value(ins_id, 42)


def get_revenue_cagr_5y(ins_id: int) -> Optional[float]:  # Omsättning(M) = 53
    hist = _kpi_history_by_id(ins_id, 53, "year", "mean")
    return _cagr(hist, years=5)


def get_ebit_cagr_5y(ins_id: int) -> Optional[float]:  # Rörelseresultat(M) = 55
    hist = _kpi_history_by_id(ins_id, 55, "year", "mean")
    return _cagr(hist, years=5)


# ------------------------
# Health & Dividend (nya helpers)
# ------------------------
def get_interest_coverage_latest(ins_id: int) -> Optional[float]:
    """
    Hämtar Interest coverage via KPI (dynamisk id-lookup).
    Försöker först 'year', sedan 'r12'.
    """
    return _kpi_value_latest_by_names(
        ins_id,
        ["Interest Coverage", "InterestCoverage", "Ränte", "Räntetäckningsgrad"],
        report_order=("year", "r12"),
    )


def get_interest_coverage_by_ticker(ticker: str) -> Optional[float]:
    ins_id = _instrument_id_by_ticker(ticker)
    if ins_id is None:
        return None
    return get_interest_coverage_latest(ins_id)


def get_payout_ratio_latest(ins_id: int) -> Optional[float]:
    """
    Hämtar Payout ratio (%) via KPI (dynamisk id-lookup).
    """
    return _kpi_value_latest_by_names(
        ins_id,
        ["Payout Ratio", "PayoutRatio", "Utdelningsandel"],
        report_order=("year", "r12"),
    )


def get_payout_ratio_by_ticker(ticker: str) -> Optional[float]:
    ins_id = _instrument_id_by_ticker(ticker)
    if ins_id is None:
        return None
    return get_payout_ratio_latest(ins_id)


def get_dividend_stability_years(ins_id: int) -> Optional[float]:
    """
    Hämtar 'Dividend Stability Years' via KPI (dynamisk id-lookup).
    Returnerar år (kan komma som float/int i API:t).
    """
    return _kpi_value_latest_by_names(
        ins_id,
        ["Dividend Stability Years", "DividendStabilityYears", "Utdelningsstabilitet"],
        report_order=("year", "r12"),
    )


def get_dividend_stability_years_by_ticker(ticker: str) -> Optional[float]:
    ins_id = _instrument_id_by_ticker(ticker)
    if ins_id is None:
        return None
    return get_dividend_stability_years(ins_id)
