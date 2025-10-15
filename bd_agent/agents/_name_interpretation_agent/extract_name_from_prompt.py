"""Module extracts the name from user prompt - name is then used for name_interpreter_agent"""

from openai import OpenAI
from bd_agent.settings import get_openai_key


SYSTEM_PROMPT = (
    "Uppgift: Välj EXAKT ETT bolagsnamn från user message."
    "Du ska utifrån user message tolka vilken del som syftar till bolagsnamn"
    "Om det finns något som ser ut som bolagsnamn men är felstavat så kan du ta det"
    "Om ingen kandidat passar, returnera null. "
    "Returnera endast den frasen du tror är bolagsnamn. Returnera exakt så som användaren skrivit."
    "Exempel på bolagsnamn är Investor B, Swedbank A, Generic Sweden AB, SSAB etc."
)

client = OpenAI(api_key=get_openai_key())


def extract_name(user_prompt: str):
    """Returns name part based on their prompt."""

    response = client.responses.create(
        model="gpt-4o",
        temperature=0.0,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.output_text
