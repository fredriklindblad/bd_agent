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
You can run BD Agent in different modes:

    python -m bd_agent ui          # Launch Streamlit interface
    python -m bd_agent cli         # Run in CLI mode
    python -m bd_agent eval-intents  # Run intent evaluation

Quick Examples
--------------
```python
>>> import bd_agent
>>> python -m bd_agent ui
-> Streamlit UI started

>>> from bd_agent import run_agent
>>> run_agent("Analyze Evolution")
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
def run_agent(prompt: str, *, return_raw: bool = False) -> dict[str, Any] | str:
    """
    Route the given user prompt to the appropriate agent and return the response.

    Parameters
    ----------
    prompt : str
        The user's natural-language query (e.g., "Screen Swedish banks").
    return_raw : bool, optional
        If True, return the structured response (dict) instead of formatted text.

    Returns
    -------
    dict | str
        The agent's output, either as a formatted string or structured dictionary.

    Notes
    -----
    This function imports and delegates to `bd_agent.router.run_agent`
    to avoid heavy dependencies loading during import time.
    """
    from .router import run_agent as _run_agent

    return _run_agent(prompt, return_raw=return_raw)
