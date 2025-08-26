# =========================
# Börsdata metrics-provider (via ticker -> ev. id)
# =========================

from typing import Any, Dict, Optional
from bd.bd_client import BorsdataClient

class FlexibleBorsdataProvider:
    """
    Försöker hitta rätt bd.bd_tools-funktioner för nyckeltal/kurser.
    - Testar både ticker och ins_id.
    - Accepterar att resultatet kan vara pydantic-modell eller dict.
    - Skriver ut vilken funktion som användes (debug).
    """
    def __init__(self, bd_client: BorsdataClient):
        self._bd = bd_client
        self._bdt = None
        
        try:
            import bd.bd_tools as bdt
            self._bdt = bdt
        except Exception:
            self._bdt = None

        if self._bdt:
            try:
                fns = [n for n in dir(self._bdt) if callable(getattr(self._bdt, n))]
                interesting = [n for n in fns if any(k in n.lower() for k in ["ratio","ratios","quote","price","key","ebit","pe"])]
                print("🔎 bd_tools tillgängliga funktioner:", ", ".join(sorted(interesting)))
            except Exception:
                pass

    def _try_call(self, name: str, *args, **kwargs) -> Optional[Any]:
        if not self._bdt or not hasattr(self._bdt, name):
            return None
        fn = getattr(self._bdt, name)
        try:
            res = fn(*args, **kwargs)
            if res:
                print(f"🔧 bd_tools: använde {name}({', '.join([str(a) for a in args])})")
            else:
                print(f"⚠️ {name}({args}) returnerade tomt")
            return res or None
        except Exception as e:
            print(f"💥 {name} fail: {e}")
            return None


    def _id_for_ticker(self, ticker: str) -> Optional[int]:
        # Stöd både dict och pydantic Instrument
        for it in getattr(self._bd, "instruments", []):
            t = it.ticker if hasattr(it, "ticker") else (it.get("ticker") if isinstance(it, dict) else None)
            if t and t.upper() == ticker.upper():
                if hasattr(it, "id"): 
                    return getattr(it, "id")
                if isinstance(it, dict):
                    return it.get("id") or it.get("ins_id") or it.get("InsId") or it.get("insId")
        return None

    # ----- Key Ratios -----
    def key_ratios_by_ticker(self, ticker: str) -> Dict[str, Any]:
        # Prova ticker-varianter
        for n in [
            "get_key_ratios_latest", "key_ratios_latest",
            "get_ratios_latest", "get_key_ratios", "key_ratios",
            "get_key_ratios_latest_by_ticker", "key_ratios_latest_by_ticker",
        ]:
            r = self._try_call(n, ticker)
            if r is not None:
                return self._coerce_key_ratios(r)

        # Prova id-varianter
        ins_id = self._id_for_ticker(ticker)
        if ins_id is not None:
            for n in [
                "get_key_ratios_latest", "key_ratios_latest",
                "get_ratios_latest", "get_key_ratios", "key_ratios",
                "get_key_ratios_latest_by_id", "key_ratios_latest_by_id",
            ]:
                r = self._try_call(n, ins_id)
                if r is not None:
                    return self._coerce_key_ratios(r)

        return {}

    # ----- Quote / Price -----
    def quote_by_ticker(self, ticker: str) -> Dict[str, Any]:
        for n in [
            "get_last_quote", "get_quote_latest", "get_quote",
            "last_quote", "quote_latest",
            "get_last_price", "get_price_latest", "get_price", "price_latest",
            "get_quote_by_ticker",
        ]:
            r = self._try_call(n, ticker)
            if r is not None:
                return self._coerce_quote(r)

        ins_id = self._id_for_ticker(ticker)
        if ins_id is not None:
            for n in [
                "get_last_quote", "get_quote_latest", "get_quote",
                "last_quote", "quote_latest",
                "get_last_price", "get_price_latest", "get_price", "price_latest",
                "get_quote_by_id",
            ]:
                r = self._try_call(n, ins_id)
                if r is not None:
                    return self._coerce_quote(r)

        return {}

    # ----- Coercers -----
    def _coerce_key_ratios(self, r: Any) -> Dict[str, Any]:
        """
        Acceptera:
          - bd_models.KeyRatios (pydantic)
          - dict
          - lista med senaste först/sist
        Returnera dict med förväntade nycklar: 'year','pe','ev_ebit','ev_sales','roic','gross_margin','ebit_margin', ev. 'asOf'
        """
        # lista? ta senaste året
        if isinstance(r, (list, tuple)) and r:
            # sortera om det finns 'year'
            try:
                r_sorted = sorted(r, key=lambda x: getattr(x, "year", x.get("year") if isinstance(x, dict) else 0), reverse=True)
            except Exception:
                r_sorted = r
            r = r_sorted[0]

        # pydantic KeyRatios?
        if hasattr(r, "model_dump") and callable(r.model_dump):
            d = r.model_dump()
        elif isinstance(r, dict):
            d = dict(r)
        else:
            # försök plocka attribut
            d = {}
            for key in ["year","pe","ev_ebit","ev_sales","roic","gross_margin","ebit_margin","asOf","date"]:
                if hasattr(r, key):
                    d[key] = getattr(r, key)

        # säkerställ nycklar
        out = {
            "year": d.get("year"),
            "PE": d.get("pe") if d.get("pe") is not None else d.get("PE"),
            "EV_EBIT": d.get("ev_ebit") if d.get("ev_ebit") is not None else d.get("EV_EBIT"),
            "EV_Sales": d.get("ev_sales") if d.get("ev_sales") is not None else d.get("EV_Sales"),
            "ROIC": d.get("roic") if d.get("roic") is not None else d.get("ROIC"),
            "GrossMargin": d.get("gross_margin") if d.get("gross_margin") is not None else d.get("GrossMargin"),
            "EbitMargin": d.get("ebit_margin") if d.get("ebit_margin") is not None else d.get("EbitMargin"),
            "asOf": d.get("asOf") or d.get("date"),
        }
        return out

    def _coerce_quote(self, r: Any) -> Dict[str, Any]:
        """
        Normalisera valfritt quote-objekt/dict till {price, marketCap}
        """
        if isinstance(r, (list, tuple)) and r:
            r = r[0]

        if hasattr(r, "model_dump") and callable(r.model_dump):
            d = r.model_dump()
        elif isinstance(r, dict):
            d = dict(r)
        else:
            d = {}
            for key in ["price","last","close","marketCap","MarketCap","mcap"]:
                if hasattr(r, key):
                    d[key] = getattr(r, key)

        return {
            "price": d.get("price") or d.get("last") or d.get("close"),
            "marketCap": d.get("marketCap") or d.get("MarketCap") or d.get("mcap"),
        }

    def enrich_metrics_from_kpis(self, ticker: str) -> Dict[str, Optional[float]]:
        ins_id = self._id_for_ticker(ticker)
        if ins_id is None:
            return {}
        from bd.bd_tools import (
            get_roic_latest, get_gross_margin_latest, get_ebit_margin_latest,
            get_netdebt_ebitda_latest, get_revenue_cagr_5y, get_ebit_cagr_5y
        )
        return {
            "ROIC": get_roic_latest(ins_id),
            "GrossMargin": get_gross_margin_latest(ins_id),
            "EbitMargin": get_ebit_margin_latest(ins_id),
            "NetDebtEbitda": get_netdebt_ebitda_latest(ins_id),
            "RevenueCagr5Y": get_revenue_cagr_5y(ins_id),
            "EbitCagr5Y": get_ebit_cagr_5y(ins_id),
        }
