"""Module is an agent that gives general investment advices or responds to general questions about finance"""

from openai import OpenAI
from bd_agent.settings import get_openai_key
import bd_agent.bd as bd


def run(user_prompt: str):
    """Runs the general investment advice agent"""
    client = OpenAI(api_key=get_openai_key())

    SYSTEM_PROMPT = """
                        You are a general investment advisor. Act like an investment and stock expert.
                        Your task is to respond to inquiries related to stocks, investments and finance.
                        For questions that is not in that field or area, please respond to the user that you
                        are expoert in finance and stocks and will not respond to other inquiries.
                        Respond concisely and pedagogically.
                    """

    response = client.responses.create(
        model="gpt-4o",
        temperature=0.7,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.output_text
