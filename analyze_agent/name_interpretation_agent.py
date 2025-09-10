# name_interpretation_agent.py
"""Pydantic Agent som tolkar user input och returnerar en dict {insId:int, name:str, ticker:str}"""

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
from rapidfuzz import process, fuzz

from bd.bd_metadata import get_nordics_instruments_info

""" CLASSES """


class CompanyInterpretation(BaseModel):
    insId: int
    name: str
    ticker: str


@dataclass
class Deps:
    best_matches: list[str]


""" AGENT """

name_agent = Agent(
    model=OpenAIChatModel("gpt-4o"),
    output_type=str,
    deps_type=Deps,
    system_prompt=(
        "Välj det mest lämpliga bolaget åt användaren. Du får ENDAST "
        "välja ett namn från listan {best_matches}. Varje bolag är ett strängelement i listan."
        "Returnera ett namn exakt så som det står i listan."
    ),  # när jag byter "måste" till "får inte" så ändras om tool används eller inte
)


@name_agent.system_prompt(dynamic=True)
def dynamic_system_prompt(ctx: RunContext[Deps]) -> str:
    # print("TPYE CTX", type(ctx.prompt), ctx.prompt)
    # print(dir(ctx.prompt))
    bm = ctx.deps.best_matches
    lines = "\n".join(f"- {name}" for name in bm)
    return (
        "Välj exakt ett bolagsnamn från listan nedan:\n"
        + lines
        + "\nReturnera namnet exakt som det står."
    )


""" AGENT RUN FUNCTION """


def run_name_interpretation_agent(user_prompt: str):
    """
    1) Låt agenten välja ETT namn från tillåten lista.
    2) Slå upp insId/ticker deterministiskt i DF.
    3) Returnera CompanyInterpretation.
    """
    print(f"\n🗨️  Fråga till name-interpretation-agenten: {user_prompt}")
    df = get_nordic_instruments_df()
    # print(df.info())
    # df_new = df[df["ticker"] == "GENI"]
    # print(df_new.head())
    names = df["name"].values.tolist()
    # print(names)
    best_matches = find_best_matches(user_prompt, names)
    deps = Deps(best_matches=best_matches)
    # print("BEST MATCHES: ", type(best_matches), best_matches)
    result = name_agent.run_sync(user_prompt, deps=deps)
    # print(dir(name_agent))
    print("\n==== RAW RESPONSE ====")
    print(result)
    print("\n=== ALL MESSAGES ===")
    print(log_model_request_response(result.all_messages()))
    print("\n=== OUTPUT ===")
    print(result.output)
    comp_dict = find_ticker_and_insId(result.output, df)
    print("\n=== FINAL RESULT ===")
    print(comp_dict)
    return None


""" helper functions below """


def find_best_matches(user_prompt: str, companies: list, n=20):
    """Return top-N matchningar baserat på fuzzy matchning"""
    matches = process.extract(
        query=user_prompt,
        choices=companies,
        scorer=fuzz.token_sort_ratio,
        limit=n,
    )
    return [match[0] for match in matches]


def get_nordic_instruments_df() -> pd.DataFrame:
    data = get_nordics_instruments_info()
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


def log_model_request_response(result_all_messages):
    ram = result_all_messages
    count = 0
    for i in ram:
        count += 1
        print(f"--------------Message {count}--------------\n", i)


def find_ticker_and_insId(company_name, df) -> dict:
    # print("\nFIND TICKER AND INSID--------------------------------------------\n")
    # print(company_name, type(company_name))
    # print(df.head)
    # print(df.info())
    selected_row = df.loc[df["name"] == company_name]
    # print("sel row", selected_row, type(selected_row))
    company_dict = selected_row.iloc[0].to_dict()
    # print(company_dict, type(company_dict))
    # print(type(selected_rows))
    return company_dict


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
