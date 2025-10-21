"""Module returns the top KPI:s for the industy of the instrument based on web research"""

import bd_agent.bd as bd
from openai import OpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from ._models import KPISuggestion
from bd_agent.agents._find_industry_kpis._helpers import validate_kpi_suggestions


def _find_industry_kpis(insId: int) -> list[KPISuggestion]:
    """funktionen är en agent som tar ett company ID som input och returnera
    en lista med relevanta KPI:er. För varje KPI finns info om:
    - namn
    - kpiId (i Börsdata)
    - rationale
    - sources
    """
    # find sector name
    sectorId = bd.get_instrument_info_by_id(insId).sectorId
    sectorName = bd.get_sectors()[sectorId]

    # find industry name
    industryId = bd.get_instrument_info_by_id(insId).industryId
    industryName = bd.get_industries()[industryId]

    # find industry companies and save in a list (can to sector too if you want)
    industry_companies = bd.get_companies_by_industry(industryId)
    industry_list = [comp["name"] for comp in industry_companies]

    system_prompt = f"""
                        Du är en investeringsanalytiker. 
                        Ditt mål är att identifiera de 5-10 nyckeltal (KPI:er) som är mest relevanta för analys 
                        av bolag inom sektorn "{sectorName}" och branschen "{industryName}". Fokusera på att ta reda på inte bara
                        generella KPI:er för bolag utan i synnerhet på sektorn "{sectorName}" och branschen "{industryName}".
                        
                        Bolag som är i denna industry och som går leta relevanta KPI:er för är: {industry_list[:20]}

                        1. Använd primärt information från välkända, trovärdiga finanskällor:
                        - Investopedia
                        - Morningstar
                        - PwC, KPMG, EY, Deloitte (industry outlooks)
                        - Bloomberg Intelligence
                        - McKinsey & Company
                        - CFA Institute, Corporate Finance Institute (CFI)
                        2. Om inget relevant finns där, sök även efter branschspecifika analyser (exempelvis 
                        'energy sector key financial ratios site:investopedia.com' eller 'consumer goods KPIs site:morningstar.com').

                        När du har tagit fram förslag på 5-10 nyckeltal, matcha dem mot denna lista och returnera det exakta namnet enligt listan för varje.
                        {bd.kpi_map}
                        
                        Returnera en sammanställning på svenska med:
                        - De 5–10 nyckeltal som är mest använda i denna bransch (id och namn)
                        - En kort beskrivning varför de är viktiga
                        - Källa för varje nyckeltal
                        """

    kpi_agent = Agent(
        model=OpenAIChatModel("gpt-4o"),
        output_type=list[KPISuggestion],
        # deps_type=
        system_prompt=system_prompt,
    )

    # kör agenten
    result = kpi_agent.run_sync()

    # # print all messages for test only
    # print(result.all_messages())

    # validate the KPI suggestion. if nothing happen its OK, else error raised
    validate_kpi_suggestions(result.output)

    # # result.output är en lista av KPISuggestions som har id, name, rationale och sources
    # print(result.output)

    return result.output
