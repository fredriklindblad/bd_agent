from __future__ import annotations

from typing import TypedDict

import pandas as pd
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from typing_extensions import TypedDict

from bd.bd_metadata import get_global_instruments_info

""" Pydantic Agent som tolkar user prompt till vilket bolag som ska analyseras"""


class CompanyInterpretation(BaseModel):
    insId: int
    name: str
    ticker: str


class Deps(TypedDict):
    names: list[str]


class NameInterpretation(BaseModel):
    name: str


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
    print("df_new   ", type(df_new.copy()))
    return df_new.copy()


name_agent = Agent(
    model=OpenAIModel("gpt-4o"),
    # deps_type=Deps,
    # output_type=NameInterpretation
    system_prompt="returnera en string med bolagsnamn",
    # system_prompt=(
    #     "Välj det mest lämpliga bolaget åt användaren, men du får ENDAST "
    #     "returnera ett bolag som finns i listan i Deps."
    #     "Returnera EXAKT ett tillåtet namn."
    # ),
)


def lookup_id_ticker_from_name(name: str, df: pd.DataFrame) -> CompanyInterpretation:
    """
    Deterministisk lookup i DF (namnet kommer från listan → bör matcha exakt).
    Hanterar ev. dubbletter genom att ta första raden.
    """
    rows = df.loc[df["name"] == name]
    if rows.empty:
        # defensivt fallback om något ändrats; försök case-insensitive
        rows = df.loc[df["name"].str.casefold() == name.casefold()]
        if rows.empty:
            raise ValueError(f"Hittar inte namnet i DF: {name!r}")

    r = rows.iloc[0]
    return CompanyInterpretation(
        insId=int(r["insId"]),
        name=str(r["name"]),
        ticker=str(r["ticker"]),
    )


def run_name_interpretation_agent(user_prompt: str):
    """
    1) Låt agenten välja ETT namn från tillåten lista.
    2) Slå upp insId/ticker deterministiskt i DF.
    3) Returnera CompanyInterpretation.
    """
    print(f"\n🗨️  Fråga till name-interpretation-agenten: {user_prompt}")
    df = get_global_instruments_df()
    # names = df["name"].values.tolist()
    # result = name_agent.run_sync(user_prompt, deps={"names": names})
    result = name_agent.run_sync(user_prompt)
    print("result from name_agent: ", result)
    # company = lookup_id_ticker_from_name(result.output, df)
    # print("efter lookup ticker id", company)
    return None
    # return company
