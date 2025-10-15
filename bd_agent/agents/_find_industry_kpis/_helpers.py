"""helpers to the find industry kpis agent"""

from ._models import KPISuggestion
import bd_agent.bd as bd


def validate_kpi_suggestions(suggestions: list[KPISuggestion]) -> None:
    """validates that name and id from LLM response match the kpi map"""
    try:
        for kpi in suggestions:
            kpiId = kpi.id
            kpiName = kpi.name
            assert bd.kpi_map[kpiId] == kpiName
    except AssertionError:
        print(f"Could not match KPI id {kpiId} to kpi name {kpiName}")

    return None
