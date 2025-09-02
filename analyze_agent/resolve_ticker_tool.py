# analyze_agent/resolve_ticker_tool.py
from typing import Dict, List, Tuple

from pydantic_ai.tools import Tool


def _best_ticker(query: str, instruments: List[Dict[str, str]]) -> str:
    q = (query or "").strip().lower()
    best: Tuple[int, str] = (0, "")
    for it in instruments:
        name = (it.get("name") or "").lower()
        ticker = (it.get("ticker") or "").lower()
        score = (
            100
            if q in (name, ticker)
            else 85
            if q in name
            else 75
            if name.startswith(q) or ticker.startswith(q)
            else 0
        )
        if score > best[0]:
            best = (score, it.get("ticker") or "")
        if best[0] == 100:
            break
    return best[1]


@Tool
def resolve_ticker_tool(query: str, *, deps=None) -> str:
    """Returnera bästa tickern för användarens text."""
    # OBS: 'deps' skickas inte med i schemat till OpenAI – det injiceras av PydanticAI
    instruments = getattr(deps, "instruments", [])
    return _best_ticker(query, instruments)
