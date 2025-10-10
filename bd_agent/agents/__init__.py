"""
bd_agents.agents — publikt API och registry för alla agents.

Publikt API:
- run_analyzer
- run_screener
- run_advicer
"""

from bd_agent.agents.analyze_agent.analyze_agent import run as run_analyzer
from bd_agent.agents.screener_agent.screener_agent import run as run_screener
from bd_agent.agents.general_investment_advice.general_investment_advice import (
    run as run_advicer,
)

__all__ = ["run_analyzer", "run_screener", "run_advicer"]

"""
    FL learning notes: python package import
    använd __init__.py i mappen för publikt API 
    om du kör import * så kommer alla moduler som börjar med _ (underscore) att ignoreras.
    
"""
