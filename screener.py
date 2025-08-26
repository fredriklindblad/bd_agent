from openai import OpenAI
from bd.config import get_openai_key
from bd.bd_tools import get_instruments
from skills.screen.metadata import (
    get_sectors_dict,
    get_countries_dict,
    get_branches_dict,
    get_markets_dict,
    get_instrument_types_dict,
)
import re
from typing import List, Optional
from bd.bd_models import Instrument
from pydantic import BaseModel

# Ladda metadata
SECTORS = get_sectors_dict()
COUNTRIES = get_countries_dict()
BRANCHES = get_branches_dict()
MARKETS = get_markets_dict()
INSTRUMENT_TYPES = get_instrument_types_dict()


class FilterParams(BaseModel):
    country: Optional[str] = None
    sector: Optional[str] = None
    market: Optional[str] = None
    branch: Optional[str] = None
    instrument_type: Optional[str] = None


def run_screener(user_prompt: str):
    client = OpenAI(api_key=get_openai_key())
    print(f"\n🗨️  Fråga till screener-agenten: {user_prompt}")

    # Skapa metadata-strängar
    country_list = ", ".join(sorted(COUNTRIES.values()))
    sector_list = ", ".join(sorted(SECTORS.values()))
    branch_list = ", ".join(sorted(BRANCHES.values()))
    market_list = ", ".join(sorted(MARKETS.values()))
    instrument_list = ", ".join(sorted(INSTRUMENT_TYPES.values()))

    system_msg = f"""
                    Du är en aktieagent som tolkar investerarens fråga och returnerar ett JSON-objekt med filtreringsparametrar:
                    - country
                    - sector
                    - market
                    - branch
                    - instrument_type

                    Returnera ENDAST ren JSON – utan kodblock eller ```-tecken.

                    🎯 Giltiga värden att använda:
                    - Countries: {country_list}
                    - Sectors: {sector_list}
                    - Branches: {branch_list}
                    - Markets: {market_list}
                    - Instrument types: {instrument_list}

                    Exempel:
                    {{"country": "Sverige", "sector": "Fastigheter", "branch": "Investmentbolag", "instrument_type": "Aktie"}}
                    """.strip()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content
    print(f"\n📬 Svar från GPT:\n{content}")

    # 🔧 Rensa bort ev. ```json eller ``` runt svaret
    content = re.sub(r"^```(?:json)?|```$", "", content.strip())

    # 🧪 Försök parsa till FilterParams
    try:
        filters = FilterParams.parse_raw(content)
        print(f"\n✅ JSON tolkad korrekt: {filters.dict()}")
    except Exception:
        print("\n❌ Kunde inte tolka svaret som JSON.")
        raise ValueError(f"Kunde inte tolka svaret från OpenAI:\n{content}")

    # Extrahera & matcha ID:n
    country_ids = [k for k, v in COUNTRIES.items() if filters.country and v.lower() == filters.country.lower()]
    sector_ids = [k for k, v in SECTORS.items() if filters.sector and v.lower() == filters.sector.lower()]
    market_ids = [k for k, v in MARKETS.items() if filters.market and v.lower() == filters.market.lower()]
    branch_ids = [k for k, v in BRANCHES.items() if filters.branch and v.lower() == filters.branch.lower()]
    instrument_types = [k for k, v in INSTRUMENT_TYPES.items() if filters.instrument_type and v.lower() == filters.instrument_type.lower()]

    # Varningsutskrift om något inte matchades
    if filters.country and not country_ids:
        print(f"⚠️  Kunde inte hitta country ID för: {filters.country}")
    if filters.sector and not sector_ids:
        print(f"⚠️  Kunde inte hitta sector ID för: {filters.sector}")
    if filters.market and not market_ids:
        print(f"⚠️  Kunde inte hitta market ID för: {filters.market}")
    if filters.branch and not branch_ids:
        print(f"⚠️  Kunde inte hitta branch ID för: {filters.branch}")
    if filters.instrument_type and not instrument_types:
        print(f"⚠️  Kunde inte hitta instrument type ID för: {filters.instrument_type}")

    print(f"\n🔍 Matchade ID:\n  Country IDs: {country_ids}\n  Sector IDs: {sector_ids}\n  Market IDs: {market_ids}\n  Branch IDs: {branch_ids}\n  Instrument types: {instrument_types}")

    instruments = get_instruments()
    filtered = filter_instruments(
        instruments,
        country_ids=country_ids or None,
        sector_ids=sector_ids or None,
        market_ids=market_ids or None,
        branch_ids=branch_ids or None,
        instrument_types=instrument_types or None
    )

    print(f"\n🎯 Antal bolag efter filtrering: {len(filtered)}")
    return filtered


def filter_instruments(
    instruments: List[Instrument],
    country_ids: List[int] = None,
    sector_ids: List[int] = None,
    market_ids: List[int] = None,
    branch_ids: List[int] = None,
    instrument_types: List[int] = None,
) -> List[Instrument]:
    """
    Filtrerar instrument baserat på metadata. Alla filter är valfria.
    """
    filtered = instruments

    if country_ids:
        filtered = [i for i in filtered if i.country_id in country_ids]
    if sector_ids:
        filtered = [i for i in filtered if i.sector_id in sector_ids]
    if market_ids:
        filtered = [i for i in filtered if i.market_id in market_ids]
    if branch_ids:
        filtered = [i for i in filtered if i.branch_id in branch_ids]
    if instrument_types:
        filtered = [i for i in filtered if i.instrument_type in instrument_types]

    return filtered
