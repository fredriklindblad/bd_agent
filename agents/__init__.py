"""
analyze_agent — verktyg för user_prompt→bolagstolkning.

Publikt API:
- run_name_interpretation_agent(user_prompt: str) -> CompanyInterpretation
- analyze_company(req: AnalyzeRequest) -> AnalyzeResponse
"""

# from .analyze_agent import run_analyze_agent
# from .name_interpretation_agent import run_name_interpretation_agent

__all__ = ["run_analyze_agent", "run_name_interpretation_agent"]

__version__ = "0.1.0"

"""
    FL learning notes: python package import
    använd __init__.py i mappen för publikt API 
    om du kör import * så kommer alla moduler som börjar med _ (underscore) att ignoreras.
    
"""
