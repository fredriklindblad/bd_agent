"""
BD Agent – AI-powered stock analysis and screening (Börsdata + OpenAI)

This package integrates data from the Börsdata API with OpenAI models using PydanticAI
to analyze and screen stocks through either a Streamlit interface or command-line tool.

Public API
----------
- run_agent(prompt: str) -> str | dict
    Execute the BD Agent router and return the generated analysis or screening response.

Command-line entry
------------------
You can run BD Agent in different modes. When in project directory use:
    python -m bd_agent ui          # Launch Streamlit interface
    python -m bd_agent cli         # Run in CLI mode
    python -m bd_agent eval-intents  # Run intent evaluation

Quick import example
--------------
```python
>>> from bd_agent import run_agent
>>> run_agent("Analyze Swedbank")
-> showing Matplotlib.Figure
"""

from importlib import metadata
from typing import Any

__all__ = ["run_agent", "__version__", "__author__"]

# ---------------------------------------------------------------
# Package metadata
# ---------------------------------------------------------------
try:
    __version__: str = metadata.version("bd_agent")
except metadata.PackageNotFoundError:
    __version__ = "1.0.0"

__author__ = "Fredrik Lindblad"

# ---------------------------------------------------------------
# Public API
# ---------------------------------------------------------------

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError(
        "OPENAI_API_KEY not found in environment variables."
        " Please set it in your .env file or environment."
    )


# ---------------------------------------------------------------
# Public API
# ---------------------------------------------------------------
def run_agent(prompt: str) -> dict[str, Any] | str:
    """
    Route the given user prompt to the appropriate agent and return the response.

    Parameters
    ----------
    prompt : str
        The user's natural-language query (e.g., "Screen Swedish banks").

    Returns
    -------
    str | Matplotlib.Figure
        The agent's output is either a text response or a Matplotlib figure.

    Notes
    -----
    This function imports and delegates to `bd_agent.router.run_agent`
    to avoid heavy dependencies loading during import time.
    """
    from .router import run_agent as _run_agent

    return _run_agent(prompt)
