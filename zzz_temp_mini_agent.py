from openai import OpenAI
from .bd_agent import settings

client = OpenAI(api_key=settings.get_openai_key())

response = client.responses.create(
    model="gpt-4o",
    input="Write a short story about a robot learning to love.",
)

print(response.output_text)
