# name_interpretation_agent.py
from __future__ import annotations

""" accessa delar i output och i egna klasser """
# Om det är en lista så använd[0] etc,
# om det är en dict så använd .get("key") etc.,
# om det är en ResponseModel tex så använd .output eller .all_messages() etc. för att få fram attribut eller metoder som kalssen har.
# Använd print(dir(...)) för att se vad som finns.

# TODO - kolla upp RunContext[Deps] - vad gör den och vrf blir inget objekt Deps class?


"""hur agenten fungerar, dvs tolkning av result.all_messages()"""
# 1. ModelRequest:  agenten skickar user prompt och systm prompt tsm med tillg tool info
# 2. ModelResponse: LLM svarar med text som innehåller tool call, anropar tool
# 2b. ToolCallPart: innehåller tool name och args som LLM bestämt
# 3. ModelRequest:  agenten anropar tool med args och skickar svar till LLM
# 4. ModelResponse: LLM svarar med ToolCallPart, vill anropa tool igen
# 5. ModelRequest:  agenten anropar tool med args och skickar svar till LLM
# 6. ModelResponse: LLM kallar på output tool och fyller enligt output typ
# 7. ModelRequest: output funktionen körs i Python och "Final result processed." returneras
#
#

""" hur agenten fungerar vad gäller användade av tools """
# 1a. om jag skriver i system prompt "får inte" använda tool_1 så används det inte
# 1b. om jag skriver "måste" använda tool_1 så används det
# 2. annat som LLM tittar på när d3et avgör om tool ska användas
#   a. namn på tool
#   b. doc string i tool
#   c. output type i tool (hjälper det för agentens output type så använder gärna)
#   d. cost för att anropa, är det en tung eller lätt funktion?
#
#

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
        "Du får använda tools print_names och do_nothing för att validera att namnet finns om du vill."
        "Returnera EXAKT ett tillåtet namn."
    ),  # när jag byter "måste" till "får inte" så ändras om tool används eller inte
)


@name_agent.tool
def do_nothing(
    ctx: RunContext[Deps],
):  # [] är bara type hint, dvs inte tvingande
    """
    Värdelöst tool som inte gör något alls.
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
    # return CompanyInterpretation(insId=1, name="Test", ticker="TST")
    return None


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
    # print("names", names)
    deps = Deps(names=names)
    # print(type(deps), deps)
    result = name_agent.run_sync(user_prompt, deps=deps)
    # print(dir(name_agent))
    print("\n==== RAW RESPONSE ====")
    print(result)
    print("\n=== ALL MESSAGES ===")
    print(log_model_request_response(result.all_messages()))
    print("\n=== OUTPUT ===")
    print(result.output)
    return None


""" helper functions below """


def log_model_request_response(result_all_messages):
    ram = result_all_messages
    count = 0
    for i in ram:
        count += 1
        print(f"--------------Message {count}--------------\n", i)
