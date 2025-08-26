import os
from this import d

from dotenv import load_dotenv

load_dotenv()


def get_bdapi_key():
    return os.getenv("BORSDATA_API_KEY")


def get_openai_key():
    return os.getenv("OPENAI_API_KEY")


def multiply(a, b):
    return a * b


def add(a, b):
    return a + b


a = 5
b = 5

c = multiply(a, b)
d = a * add(a, b)
