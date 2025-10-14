"""module returns the top KPI:s for the industy of the instrument based on web research"""

import bd_agent.bd as bd


def _find_industry_kpis(insId: int):
    sectorId = bd.get_instrument_info_by_id(insId).sectorId
    sectorName = bd.get_sectors()[sectorId]
    print("Sector name", sectorName)
    branchId = bd.get_instrument_info_by_id(insId).branchId
    branchName = bd.get_branch()[branchId]
    print("Branch name", branchName)

    # TODO agenten ska hitta secotr och bransch. Sedan ska en LLM utifrån sector branch och lsita av alla boalg i sektor/branch,
    # TODO hitta vilka som är key parameters för branschen.
