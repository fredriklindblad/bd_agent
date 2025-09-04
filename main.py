from agent import ask_agent
from analyze_agent import run_name_interpretation_agent


def main():
    user_prompt = input(
        "🧠 Skriv din fråga. Du kan:\n(1) analysera enskilt bolag\n(2) screena bolag inom bransch och land\n(3) se och analysera din portfölj\n>> "
    )
    ask_agent(user_prompt)


if __name__ == "__main__":
    # main()
    run_name_interpretation_agent("analysera generic sweden ab")


# TODO - steg 1 att classifier får tolka vad man vill göra, steg 2 att i analyze så får LLM ta ut enbart bolagsnmanet. steg 3 matchning på ngot effektivt asätt...
