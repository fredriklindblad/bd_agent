from __future__ import annotations

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.run import AgentRunResult

from bd.bd_metadata import get_global_instruments_info
from bd.bd_models import CompanyInterpretation

""" funktion för att tolka user prompt till vilket bolag som ska analyseras"""


def run_name_interpretation_agent(user_prompt: str) -> AgentRunResult:
    print(f"\n🗨️  Fråga till name-interpretation-agenten: {user_prompt}")
    model = OpenAIModel("gpt-4o")
    system_prompt = """
                        Du är en namntolkningsagent. Du ska hjälpa till att matcha användarens prompt
                        till en bästa matchning från listan i deps.
                        Du har fått en lista med bolag som deps i vilken du ska matcha user prompt till det
                        troligaste alternativet som användaren syftar på.
                        Returnera ETT bolag enligt output type.
                    """
    name_agent = Agent(
        model=model,
        output_type=CompanyInterpretation,
        deps_type=get_global_instruments_info()["name"].tolist(),
        system_prompt=system_prompt,
    )
    result = name_agent.run_sync(user_prompt)
    print(result)
    insId = result.output
    print(insId)
    print(type(insId))
    # print(result["insId"])
    return insId
