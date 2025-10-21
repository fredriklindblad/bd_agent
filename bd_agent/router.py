"""Router that is called from __main__.py and routes forward to the correct agent"""

from bd_agent.intents import intent_classifier
import bd_agent.agents as agents
from bd_agent.agents._find_industry_kpis.__find_industry_kpis import (
    _find_industry_kpis,
)
import bd_agent.bd as bd


def run_agent(user_prompt) -> None:  # TODO - fix print format and type hint
    """Runs the agent through intent and direct to the right agent.
    Then prints the output.
    """
    # TODO either use below user_prompt or user_prompt as argument to run_agent above
    # # Take input from user
    # user_prompt = input("What can I help you with today?\n>>")

    # Classify user prompt
    intent = intent_classifier(user_prompt).intent

    # route forward to right agent based on intent
    if intent == "screening":
        # print("Routing to screening...")
        return agents.run_screener(user_prompt)
    elif intent == "single_stock_analysis":
        # print("Routing to single stock analysis...")
        return agents.run_analyzer(user_prompt)
    elif intent == "portfolio_analysis":
        # print("Routing to portfolio analysis...")
        pass
    elif intent == "general_investment_advice":
        # print("Routing to general investment advice...")
        return agents.run_advisor(user_prompt)
    else:
        return "I am not an expert on this subject. Please ask me about stocks, finance or investments and I am happy to help :)"
