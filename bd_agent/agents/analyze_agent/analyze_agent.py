"""Analyze agent that analyzes a specific company and returns a visualization of the top KPI:s
for companies in the industry it operates"""

from __future__ import annotations

from bd_agent.agents._name_interpretation_agent.name_interpretation_agent import (
    run as run_name_interpretation_agent,
)
from bd_agent.bd import BorsdataClient, kpis_json_to_df, get_instrument_info_by_id
from bd_agent.agents._find_industry_kpis.__find_industry_kpis import (
    _find_industry_kpis,
)
from ._helpers import filter_relevant_kpis, create_kpis_report


def run(user_prompt: str):
    """Function takes a user prompt and returns diagrams over relevant KPI's for the company"""
    # interpret company id from user prompt
    insId = run_name_interpretation_agent(user_prompt).insId

    # call bd api and create df of kpis
    bd = BorsdataClient()
    kpis_json = bd.get_instrument_kpi(insId=insId)
    ins_df = kpis_json_to_df(kpis_json)

    # find the industry KPI based on instrument ID
    rel_kpis = _find_industry_kpis(insId)

    # filter df for relevant kpis
    df_subset = filter_relevant_kpis(ins_df, rel_kpis)

    # create report for the relevant kpis
    create_kpis_report(df_subset, insId, rel_kpis)
