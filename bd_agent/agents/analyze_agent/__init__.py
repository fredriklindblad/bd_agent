"""
analyze_agent — verktyg för user_prompt→bolagstolkning.

Publikt API:
- run
"""

from bd_agent.agents.analyze_agent import run

__all__ = ["run"]


"""
    FL learning notes: python package import
    använd __init__.py i mappen för publikt API 
    om du kör import * så kommer alla moduler som börjar med _ (underscore) att ignoreras,
    men bättre vara explicit med __all__ = [....]
    
"""
