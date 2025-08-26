from agent import ask_agent

def main():
    user_prompt = input("🧠 Skriv din fråga. Du kan:\n(1) analysera enskilt bolag\n(2) screena bolag inom bransch och land\n(3) se och analysera din portfölj\n>> ")
    ask_agent(user_prompt)

if __name__ == "__main__":
    main()
