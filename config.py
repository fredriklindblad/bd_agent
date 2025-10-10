# Konfiguration för API-nycklar

import os

from dotenv import load_dotenv

load_dotenv()


def get_bdapi_key():
    return os.getenv("BORSDATA_API_KEY")


def get_openai_key():
    return os.getenv("OPENAI_API_KEY")
