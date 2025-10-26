"""
name_interpretation_agent.py

Pydantic Agent that interprets user input and returns a dict {insId:int, name:str, ticker:str}

"""

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

from bd_agent.bd import BorsdataClient

from .extract_name_from_prompt import extract_name

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
        "Utifrån användarens meddelande ska du först tolka vilken del som är ett bolagsnamn."
        "Du kommer i nästa systemmeddelande få en lista med bolagsnamn."
        "Du får ENDAST välja ett namn från den lista du får i nästa systemmeddelande."
        "Returnera ett namn exakt så som det står i listan."
    ),
)


@name_agent.system_prompt(dynamic=True)
def dynamic_system_prompt(ctx: RunContext[Deps]) -> str:
    bm = ctx.deps.best_matches
    lines = "\n".join(f"- {name}" for name in bm)
    return (
        "Välj exakt ett bolagsnamn från listan nedan:\n"
        + lines
        + "\nReturnera namnet exakt som det står."
    )


""" AGENT RUN FUNCTION """


def run(user_prompt: str) -> CompanyInterpretation:
    """
    1) Agenten tar user prompt
    2) Agenten hämtar en lista av bolagsnamn från nordic_instruments, dvs BD API.


    Låt agenten välja ETT namn från tillåten lista.
    2) Slå upp insId/ticker deterministiskt i DF.
    3) Returnera CompanyInterpretation.
    """

    # extract name from total user prompt
    extracted_name = extract_name(user_prompt)

    df = get_nordic_instruments_df()  # skapar en df med insId, name, ticker från BD API
    names = df["name"].values.tolist()  # skapar en lista med alla bolagsnamn
    best_matches = find_best_matches(extracted_name, names)  # hitta top-N matchningar
    deps = Deps(best_matches=best_matches)  # best matches är en lista med str

    """Kör agenten och printa resulatet"""
    result = name_agent.run_sync(extracted_name, deps=deps)
    # print("\n==== RAW RESPONSE ====")
    # print(result)
    # print("\n=== COST & USAGE ===")
    # print(result.usage())
    # print("\n=== ALL MESSAGES ===")
    # print(log_model_request_response(result.all_messages()))
    # print("\n=== OUTPUT ===")
    # print(result.output)
    comp_dict = find_ticker_and_insId(result.output, df)  # TICK och INSID från df
    # print("\n=== FINAL RESULT ===")
    # print(CompanyInterpretation(**comp_dict))  # access del genom .InsId etc
    return CompanyInterpretation(**comp_dict)


""" helper functions below """


def find_best_matches(extracted_name: str, companies: list, n=20):
    """Return top-N matchningar baserat på fuzzy matchning"""
    matches = process.extract(
        query=extracted_name,
        choices=companies,
        scorer=fuzz.token_sort_ratio,
        limit=n,
    )
    return [match[0] for match in matches]


def get_nordic_instruments_df() -> pd.DataFrame:
    instruments = BorsdataClient().get_nordic_instruments()
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
            "industryId",
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
    """Takes company name and dataframe. Returns dict with insId, name, ticker for the company."""
    selected_row = df.loc[df["name"] == company_name]
    company_dict = selected_row.iloc[0].to_dict()
    return company_dict
