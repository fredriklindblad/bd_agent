import requests

from bd.config import get_bdapi_key

BASE_URL = "https://apiservice.borsdata.se/v1"

# # -----------------------------------------------
# # Funktioner för att hämta instrumentlista
# # -----------------------------------------------


def get_global_instruments_info() -> dict:
    """Returnerar en JSON med info om globala instrument från bd request"""
    url = f"{BASE_URL}/instruments/global?authKey={get_bdapi_key()}"
    response = requests.get(url)
    data = response.json()
    print(type(data))
    return data


# def get_nordics_instruments_info(insId=1) -> Dict[int, str]:
#     """Returnerar en JSON med info om nordiska instrument från bd request"""
#     url = f"{BASE_URL}/instruments?authKey={get_bdapi_key()}"
#     response = requests.get(url)
#     data = response.json()
#     return data


# -----------------------------------------------
# Funktioner för att hämta metadata
# -----------------------------------------------


# def get_sectors_dict() -> Dict[int, str]:
#     """Returnerar dict med {sectorId: sectorName}"""
#     url = f"{BASE_URL}/sectors?authKey={get_bdapi_key()}"
#     response = requests.get(url)
#     data = response.json()
#     return {s["id"]: s["name"] for s in data.get("sectors", [])}


# def get_countries_dict() -> Dict[int, str]:
#     """Returnerar dict med {countryId: countryName}"""
#     url = f"{BASE_URL}/countries?authKey={get_bdapi_key()}"
#     response = requests.get(url)
#     data = response.json()
#     return {c["id"]: c["name"] for c in data.get("countries", [])}


# def get_markets_dict() -> Dict[int, str]:
#     """Returnerar dict med {marketId: marketName}"""
#     url = f"{BASE_URL}/markets?authKey={get_bdapi_key()}"
#     response = requests.get(url)
#     data = response.json()
#     return {m["id"]: m["name"] for m in data.get("markets", [])}


# def get_branches_dict() -> Dict[int, str]:
#     url = f"{BASE_URL}/branches?authKey={get_bdapi_key()}"
#     response = requests.get(url)
#     data = response.json()
#     return {b["id"]: b["name"] for b in data.get("branches", [])}


# def get_instrument_types_dict() -> Dict[int, str]:
#     """Returnerar dict med {instrumentTypeId: typeName}"""
#     return {
#         0: "Aktie",
#         1: "Fond",
#         2: "ETF",
#         3: "Index",
#         4: "Pref",
#         5: "SPAC",
#         6: "Börshandlad fond",
#         99: "Övrigt",
#     }
