"""Module returns the top KPI:s for the industy of the instrument based on web research"""

import bd_agent.bd as bd
from openai import OpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from ._models import KPISuggestion


def _find_industry_kpis(insId: int):
    # find sector name
    sectorId = bd.get_instrument_info_by_id(insId).sectorId
    sectorName = bd.get_sectors()[sectorId]

    # find branch name
    branchId = bd.get_instrument_info_by_id(insId).branchId
    branchName = bd.get_branches()[branchId]

    # find branch companies and save in a list (can to sector too if you want)
    branch_companies = bd.get_companies_by_branch(branchId)
    branch_list = [comp["name"] for comp in branch_companies]

    system_prompt = f"""
                        Du är en investeringsanalytiker. 
                        Ditt mål är att identifiera de nyckeltal (KPI:er) som är mest relevanta för analys 
                        av bolag inom sektorn "{sectorName}" och branschen "{branchName}".
                        
                        Bolag som är i denna branch och som går leta relevanta KPI:er för är: {branch_list[:20]}

                        1. Använd primärt information från välkända, trovärdiga finanskällor:
                        - Investopedia
                        - Morningstar
                        - PwC, KPMG, EY, Deloitte (industry outlooks)
                        - Bloomberg Intelligence
                        - McKinsey & Company
                        - CFA Institute, Corporate Finance Institute (CFI)
                        2. Om inget relevant finns där, sök även efter branschspecifika analyser (exempelvis 
                        'energy sector key financial ratios site:investopedia.com' eller 'consumer goods KPIs site:morningstar.com').

                        Returnera en sammanställning med:
                        - De 5–10 nyckeltal som är mest använda i denna bransch
                        - En kort beskrivning varför de är viktiga
                        - Källa för varje nyckeltal
                        """

    kpi_agent = Agent(
        model=OpenAIChatModel("gpt-4o"),
        output_type=list[KPISuggestion],
        # deps_type=
        system_prompt=system_prompt,
    )

    result = kpi_agent.run_sync()
    for kpi in result.output:
        print(kpi.name)

    # print(result.all_messages())

    # TODO fuzzy matcha mot min egen lista - gör det med en @decorator system prompt så som du gjorde i names. Eller kan vi ta in hela på 150 namn?

    # TODO agenten ska hitta secotr och bransch. Sedan ska en LLM utifrån sector branch och lsita av alla boalg i sektor/branch hitta vilka som är key parameters för branschen.
