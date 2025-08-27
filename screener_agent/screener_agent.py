# screener_agent/screener.py

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from bd.bd_client import BorsdataClient
from bd.bd_metadata import (
    get_branches_dict,
    get_countries_dict,
    get_instrument_types_dict,
    get_markets_dict,
    get_sectors_dict,
)
from screener_agent.models import (
    ScreenerFilterRequest,
    ScreenerResponse,
)


def run_screener(user_prompt: str) -> ScreenerResponse:
    # 1) Ladda metadata (för att instruera agenten med giltiga värden)
    SECTORS = get_sectors_dict()
    COUNTRIES = get_countries_dict()
    BRANCHES = get_branches_dict()
    MARKETS = get_markets_dict()
    INSTRUMENT_TYPES = get_instrument_types_dict()

    country_list = ", ".join(sorted(COUNTRIES.values()))
    sector_list = ", ".join(sorted(SECTORS.values()))
    branch_list = ", ".join(sorted(BRANCHES.values()))
    market_list = ", ".join(sorted(MARKETS.values()))
    instrument_list = ", ".join(sorted(INSTRUMENT_TYPES.values()))

    # 2) Systemprompt: BE om FILTER (inte resultatlista!)
    system_prompt = f"""
                        Du är en aktiescreener som TOLKAR investerarens fråga och returnerar ett JSON-objekt med filtreringsparametrar:
                        - country
                        - sector
                        - market
                        - branch
                        - instrument_type

                        Returnera ENDAST ren JSON – utan kodblock eller ```-tecken.

                        🎯 Giltiga värden (använd EXAKT dessa strängar när de är relevanta):
                        - Countries: {country_list}
                        - Sectors: {sector_list}
                        - Branches: {branch_list}
                        - Markets: {market_list}
                        - Instrument types: {instrument_list}

                        Exempel:
                        {{"country": "Sverige", "sector": "Finans & Fastighet", "branch": "Banker", "instrument_type": "Aktie"}}
                        """.strip()

    # 3) Agenten som bara tolkar filter → ScreenerFilterRequest
    model = OpenAIModel("gpt-4o")
    filter_agent = Agent(
        model=model,
        output_type=ScreenerFilterRequest,
        system_prompt=system_prompt,
    )

    print(f"\n🗨️  Fråga till screener-agenten: {user_prompt}")

    # 4) Kör synkront: hämta filtren via .output
    filter_run = filter_agent.run_sync(user_prompt)
    filters: ScreenerFilterRequest = filter_run.output
    print(f"📎 Tolkade filter: {filters.model_dump()}")

    # 5) Hämta faktiska bolag från Börsdata via din klient
    bd_client = BorsdataClient()
    stocks = bd_client.screen(
        country_name=filters.country,
        sector_name=filters.sector,
        market_name=filters.market,
        branch_name=filters.branch,
        instrument_type_name=filters.instrument_type,
        # limit=200,  # valfritt om du vill begränsa
    )  # -> List[ScreenerStockResult]

    # 6) Wrappa i ScreenerResponse och returnera
    response = ScreenerResponse(results=stocks)
    print(f"\n📊 Screener-resultat: {len(response.results)} bolag")
    print("Första 100:")
    for r in response.results[:100]:
        print(f"{r.ticker:10} {r.name:40} {r.sector or ''} / {r.branch or ''}")

    return response
