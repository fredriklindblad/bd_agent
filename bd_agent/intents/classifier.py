"""Consists of IntentClassification basemodel and a function intent_classfier() -> IntentClassification"""

from typing import Literal
from pydantic import BaseModel
from openai import OpenAI
from bd_agent.settings import get_openai_key


class IntentClassification(BaseModel):
    intent: Literal[
        "screening",
        "single_stock_analysis",
        "portfolio_analysis",
        "general_investment_advice",
        "None",
    ]
    confidence: float
    reasoning: str


client = OpenAI(api_key=get_openai_key())


SYSTEM_PROMPT = """
                    You are an AI agent that classifies what the user wants to do in an investment assistant.

                    You have the following options:
                    1. "screening" — if the user wants to find companies based on filters
                    such as industry, country, sector, or key financial metrics.

                    2. "single_stock_analysis" — if the user wants to analyze a single company
                    (e.g., asking about a specific stock).

                    3. "portfolio_analysis" — if the user wants to analyze a portfolio or multiple holdings
                    (e.g., asking about diversification or opinions on multiple stocks).

                    4. "investment_advice" — if the user wants investment advice or strategies or gain knowledge about finance, stocks or investments.

                    Your task is to classify the user's intent based on their prompt.
                    You should also provide a brief reasoning for your classification. Be concise.
                    You should also provide "confidence" (a float between 0 and 1) indicating how sure you are about the classification.
                    If you are not at least 50% confident in your classification, return "None" as the intent.

                    You should return a JSON object with the fields "intent", "confidence", and "reasoning".
                """


def intent_classifier(user_prompt: str) -> IntentClassification:
    """Classifies the user's intent based on their prompt."""

    response = client.responses.parse(
        model="gpt-4o",
        temperature=0.0,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        text_format=IntentClassification,
    )

    out = response.output[0].content[0].parsed

    return out
