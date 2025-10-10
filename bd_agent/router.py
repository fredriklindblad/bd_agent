"""Router that is called from __main__.py and routes forward to the correct agent"""

from bd_agent.intents import intent_classifier
import bd_agent.agents as agents


def run_agent() -> None:  # TODO - fix print format and type hint
    """Runs the agent through intent and direct to the right agent.
    Then prints the output.
    """

    # Take input from user
    user_prompt = input("What can I help you with today?\n>>")

    # Classify user prompt
    intent = intent_classifier(user_prompt).intent

    # route forward to right agent based on intent
    if intent == "screening":
        return agents.run_screener(user_prompt)
    elif intent == "single_stock_analysis":
        return agents.run_analyzer(user_prompt)
    elif intent == "portfolio_analysis":
        pass
    elif intent == "general_investment_advice":
        pass
    else:
        return "Could not assess intent. Please retry."
