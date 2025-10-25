"""
agents — public API for all the agents within the bd_agent

Public API:
- run_analyzer
- run_screener
- run_advicer
"""

from .analyze_agent.analyze_agent import run as run_analyzer
from .screener_agent.screener_agent import run as run_screener
from .advisor_agent.general_investment_advice import (
    run as run_advisor,
)

__all__ = ["run_analyzer", "run_screener", "run_advisor"]

"""
    FL learning notes: python package import
    använd __init__.py i mappen för publikt API 
    om du kör import * så kommer alla moduler som börjar med _ (underscore) att ignoreras.
    
"""
