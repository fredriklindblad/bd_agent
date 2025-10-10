# Configurations for the BD and OPENAI API keys

import os


def get_bdapi_key() -> str | None:
    """Retrieves the Börsdata API key from environment variables or .env file."""
    return os.getenv("BORSDATA_API_KEY")


def get_openai_key() -> str | None:
    """Retrieves the OpenAI API key from environment variables or .env file."""
    return os.getenv("OPENAI_API_KEY")
