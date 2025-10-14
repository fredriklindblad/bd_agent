"""Models to the find industry kpis agent"""

from pydantic import BaseModel


class KPISuggestion(BaseModel):
    name: str
    rationale: str
    source: str
