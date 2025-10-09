import os
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel

from bd.config import get_openai_key


class IntentClassification(BaseModel):
    intent: Literal[
        "screening",  # Ex: 'Hitta svenska teknikbolag'
        "single_stock_analysis",  # Ex: 'Vad tycker du om Evolution?'
        "portfolio_analysis",  # Ex: 'Hur ser min portfölj ut?'
        "None",
    ]
    confidence: float  # LLM's säkerhet
    reasoning: str  # Förklaring till klassificeringen


def classify_prompt(user_prompt: str) -> IntentClassification:
    client = OpenAI(api_key=get_openai_key())
    system_prompt = """
                        Du är en AI-agent som klassificerar vad användaren vill göra i en investeringsassistent.

                        Du ska returnera en JSON med fältet "intent" som kan vara ett av följande:

                        - "screening" — om användaren vill hitta bolag utifrån filter som bransch, land, sektor eller nyckeltal.
                        - "single_stock_analysis" — om användaren vill analysera ett enskilt bolag (t.ex. fråga om en viss aktie).
                        - "portfolio_analysis" — om användaren vill analysera en portfölj eller flera innehav (t.ex. fråga om riskspridning eller omdöme om flera aktier).
                        - "general_investment_advice" — om användaren vill ha allmänna investeringsråd eller strategier.
                        Returnera även "confidence" (en float mellan 0 och 1) som anger hur säker du är på klassificeringen, samt "reasoning" där du kort förklarar varför du valde just denna intent.
                        Om confidence inte är över 50 %, returnera "None" som intent.
                        Returnera en korrekt formaterad JSON enligt modellen samt din rationale till klassificeringen.
                    """
    response = client.responses.parse(
        model="gpt-4.1",
        temperature=0.0,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        text_format=IntentClassification,
    )
    print(
        f"\n🧠 Klassificering: {response.output_parsed.intent} (📈 confidence: {response.output_parsed.confidence})"
    )
    print(f"🧩 Resonemang: {response.output_parsed.reasoning}")
    return response.output_parsed.intent
