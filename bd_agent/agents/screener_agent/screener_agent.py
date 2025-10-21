"""Module is the screener agent. The agent returns a df of companies based on screening criteria."""

import bd_agent.bd as bd
import pandas as pd
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from bd_agent.settings import get_openai_key


""" MODELS """


@dataclass
class Deps:
    pass


""" AGENT """

screener_agent = Agent(
    model=OpenAIChatModel("gpt-4o"),
    output_type=str,
    deps_type=Deps,
    system_prompt=(
        """
            Screen stocks based on the user prompt.
        """
    ),
)


def run(user_prompt: str):
    """Runs the screening agent."""
    bd_client = bd.BorsdataClient()
    df = pd.DataFrame(bd_client.get_nordic_instruments())

    return f"Returning {df.info()} from function."
