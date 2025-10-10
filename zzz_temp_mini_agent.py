from openai import OpenAI
from . import config

client = OpenAI(api_key=config.get_openai_key())

response = client.responses.create(
    model="gpt-4o",
    input="Write a short story about a robot learning to love.",
)

print(response.output_text)
