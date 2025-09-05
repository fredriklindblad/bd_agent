# name_interpretation_agent.py

# TODO - försök testa dig fram hur tools anropas och försök se om vi kan få agenten
# att bara använda tools om de verkligen behöver. Dvs inte alltid anropa sina tools.
# Du behöver förstå vad agenten gör i detalj.

# Om det är en lista så använd[0] etc,
# om det är en dict så använd .get("key") etc.,
# om det är en ResponseModel tex så använd .output eller .all_messages() etc. för att få fram attribut eller metoder som kalssen har.
# Använd print(dir(...)) för att se vad som finns.

# TODO - kolla upp RunContext[Deps] - vad gör den och vrf blir inget objekt Deps class?


from __future__ import annotations

from typing import TypedDict

import pandas as pd
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.messages import (
    ModelResponse,
    ModelRequest,
    ToolCallPart,
    BuiltinToolCallPart,
    ToolCallPartDelta,
    BuiltinToolReturnPart,
)

from dataclasses import dataclass

from bd.bd_metadata import get_global_instruments_info

""" Pydantic Agent som tolkar user prompt till vilket bolag som ska analyseras"""


class CompanyInterpretation(BaseModel):
    insId: int
    name: str
    ticker: str


@dataclass
class Deps:
    names: list[str]


def get_global_instruments_df() -> pd.DataFrame:
    data = get_global_instruments_info()
    instruments = data["instruments"]
    df_raw = pd.DataFrame(instruments)
    df_new = df_raw.drop(
        columns=[
            "urlName",
            "instrument",
            "isin",
            "yahoo",
            "sectorId",
            "countryId",
            "marketId",
            "branchId",
            "listingDate",
            "stockPriceCurrency",
            "reportCurrency",
        ]
    )
    return df_new.copy()


name_agent = Agent(
    model=OpenAIChatModel("gpt-4o"),
    deps_type=Deps,
    output_type=CompanyInterpretation,
    system_prompt=(
        "Välj det mest lämpliga bolaget åt användaren, men du får ENDAST "
        "returnera ett bolag som finns i listan i Deps."
        "Du måste använda toolet lookup_id_ticker_from_name för att validera att namnet finns."
        "Returnera EXAKT ett tillåtet namn."
    ),  # när jag byter "måste" till "får inte" så ändras om tool används eller inte
)


@name_agent.tool
def lookup_id_ticker_from_name(
    ctx: RunContext[Deps],
) -> CompanyInterpretation:  # [] är bara type hint, dvs inte tvingande
    """
    Deterministisk lookup i names list (namnet kommer från listan → bör matcha exakt).
    Hanterar ev. dubbletter genom att ta första raden.
    """
    print("ctx names", type(ctx.deps))
    # print("ctx names", ctx.deps.get("names"))
    # for i in names:
    #     if i.lower() == name.lower():
    #         df = get_global_instruments_df()
    #         row = df[df["name"].str.lower() == name.lower()].iloc[0]
    #         return CompanyInterpretation(
    #             insId=row["insId"], name=row["name"], ticker=row["ticker"]
    #         )
    return CompanyInterpretation(insId=1, name="Test", ticker="TST")


@name_agent.tool
def print_names(ctx: RunContext[Deps]) -> str:
    print("hej")


def run_name_interpretation_agent(user_prompt: str):
    """
    1) Låt agenten välja ETT namn från tillåten lista.
    2) Slå upp insId/ticker deterministiskt i DF.
    3) Returnera CompanyInterpretation.
    """
    print(f"\n🗨️  Fråga till name-interpretation-agenten: {user_prompt}")
    df = get_global_instruments_df()
    names = df["name"].values.tolist()[:10]
    print("names", names)
    deps = Deps(names=names)
    print(type(deps), deps)
    result = name_agent.run_sync(user_prompt, deps=deps)
    # print(dir(name_agent))
    print("\n==== RAW RESPONSE ====")
    print(result)
    print("\n=== OUTPUT ===")
    print(result.output)
    print("\n=== ALL MESSAGES ===")
    print(result.all_messages())
    print("\n==== TOOLS ====")
    for i in result.all_messages()[1].parts:
        print(i.tool_name)
    # company = lookup_id_ticker_from_name(result.output, df)
    # print("efter lookup ticker id", company)
    return None
    # return company
