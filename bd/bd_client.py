# screener_agent/client.py

import os
from typing import Optional


class BorsdataClient:
    def __init__(self, api_key: Optional[str] = None):
        if api_key is None:
            api_key = os.getenv("BORSDATA_API_KEY")
        self.api_key = api_key


# from bd_metadata import (
#     get_branches_dict,
#     get_countries_dict,
#     get_sectors_dict,
# )

# from ..screener_agent.models import ScreenerFilterRequest, ScreenerStockResult


#     # Ladda metadata en gång och bygg inversa mappar (namn -> id)
#     self.SECTORS: Dict[int, str] = get_sectors_dict()
#     self.COUNTRIES: Dict[int, str] = get_countries_dict()
#     self.BRANCHES: Dict[int, str] = get_branches_dict()

#     # Hämta universum
#     self.instruments = self._coerce_instruments(get_nordics_instruments())

# def _coerce_instruments(self, items: Iterable) -> List[Dict[str, Any]]:
#     """
#     Tål både objekt och dict från get_global_instruments(). Returnerar dict med förväntade fält.
#     Förväntade fält: ins_id, ticker, name, country_id, sector_id, branch_id, market, instrument_type_name
#     """
#     out = []
#     for it in items:
#         if isinstance(it, dict):
#             get = it.get
#         else:
#             get = lambda k: getattr(it, k, None)

#         out.append(
#             {
#                 "ins_id": get("insId") or get("InsId") or get("id") or get("InsID"),
#                 "ticker": get("ticker"),
#                 "name": get("name"),
#                 "country_id": get("country_id"),
#                 "sector_id": get("sector_id"),
#                 "branch_id": get("branch_id"),
#                 "market": get("market"),
#                 "instrument_type_name": get("instrument_type_name"),
#             }
#         )
#     return out

# # ✅ Publik metod som din agent anropar
# def screen(
#     self,
#     *,
#     country_name: Optional[str] = None,
#     sector_name: Optional[str] = None,
#     market_name: Optional[str] = None,
#     branch_name: Optional[str] = None,
#     instrument_type_name: Optional[str] = None,
#     limit: Optional[int] = None,
# ) -> List[ScreenerStockResult]:
#     filters = ScreenerFilterRequest(
#         country=country_name,
#         sector=sector_name,
#         market=market_name,
#         branch=branch_name,
#         instrument_type=instrument_type_name,
#     )
#     return self.filter_instruments(filters, limit=limit)

# def filter_instruments(
#     self, filters: ScreenerFilterRequest, *, limit: Optional[int] = None
# ) -> List[ScreenerStockResult]:
#     filtered = self.instruments

#     # Land: exakt namn -> id
#     if filters.country:
#         cid = self.COUNTRY_BY_NAME.get(_norm(filters.country))
#         if cid is not None:
#             filtered = [i for i in filtered if i.get("country_id") == cid]
#         else:
#             print(f"⚠️ Kunde inte hitta country ID för '{filters.country}'")
#             filtered = []

#     # Sektor
#     if filters.sector and filtered:
#         sid = self.SECTOR_BY_NAME.get(_norm(filters.sector))
#         if sid is not None:
#             filtered = [i for i in filtered if i.get("sector_id") == sid]
#         else:
#             print(f"⚠️ Kunde inte hitta sector ID för '{filters.sector}'")
#             filtered = []

#     # Bransch
#     if filters.branch and filtered:
#         bid = self.BRANCH_BY_NAME.get(_norm(filters.branch))
#         if bid is not None:
#             filtered = [i for i in filtered if i.get("branch_id") == bid]
#         else:
#             print(f"⚠️ Kunde inte hitta branch ID för '{filters.branch}'")
#             filtered = []

#     # Lista/marknad – exakt normaliserad match
#     if filters.market and filtered:
#         m = _norm(filters.market)
#         filtered = [i for i in filtered if _norm(i.get("market")) == m]

#     # Instrumenttyp – exakt normaliserad match
#     if filters.instrument_type and filtered:
#         t = _norm(filters.instrument_type)
#         filtered = [
#             i for i in filtered if _norm(i.get("instrument_type_name")) == t
#         ]

#     # Stabil sortering och ev. limit
#     filtered.sort(key=lambda x: (x.get("ticker") or "").upper())
#     if isinstance(limit, int) and limit >= 0:
#         filtered = filtered[:limit]

#     # Bygg modellobjekt
#     results: List[ScreenerStockResult] = []
#     for s in filtered:
#         results.append(
#             ScreenerStockResult(
#                 ticker=s.get("ticker") or "",
#                 name=s.get("name") or "",
#                 country=self.COUNTRIES.get(s.get("country_id")),
#                 sector=self.SECTORS.get(s.get("sector_id")),
#                 branch=self.BRANCHES.get(s.get("branch_id")),
#             )
#         )
#     return results
