from actions.portfolio import run_portfolio
from analyze_agent.analyze_agent import run_analyze
from general_investment_advice.general_investment_advice import (
    run_general_investment_advice,
)
from intents.classifier import classify_prompt
from screener_agent.screener_agent import run_screener


def ask_agent(user_prompt: str):
    print(f"\n🗨️  Fråga till agenten: {user_prompt}")

    # Klassificera användarens prompt
    intent = classify_prompt(user_prompt)

    # Beroende på klassificeringen, kör rätt funktion
    if intent == "screening":
        return run_screener(user_prompt)
    elif intent == "single_stock_analysis":
        return run_analyze(user_prompt)
    elif intent == "portfolio_analysis":
        return run_portfolio(user_prompt)
    elif intent == "general_investment_advice":
        return run_general_investment_advice(user_prompt)
    else:
        return "🚫 Kunde inte avgöra vad du vill göra. Förklara tydligare om du vill screena, analysera bolag eller din portfölj."
