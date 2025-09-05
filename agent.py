from analyze_agent import run_name_interpretation_agent
from intents.classifier import classify_prompt
from screener_agent import run_screener


def ask_agent(user_prompt: str):
    print(f"\n🗨️  Fråga till agenten: {user_prompt}")

    # Klassificera användarens prompt
    intent = classify_prompt(user_prompt)

    # Beroende på klassificeringen, kör rätt funktion
    if intent == "screening":
        return run_screener(user_prompt)
    elif intent == "single_stock_analysis":
        return run_name_interpretation_agent(user_prompt)
    elif intent == "portfolio_analysis":
        pass
    elif intent == "general_investment_advice":
        pass
    else:
        return "🚫 Kunde inte avgöra vad du vill göra. Förklara tydligare om du vill screena, analysera bolag eller din portfölj."


# TODO - steg 1 att classifier får tolka vad man vill göra, steg 2 att i analyze så får LLM ta ut enbart bolagsnmanet. steg 3 matchning på ngot effektivt asätt...
