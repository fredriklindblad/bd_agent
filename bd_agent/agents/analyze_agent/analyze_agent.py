# analyze_agent/analyze_agent.py
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
    """ """
    # interpret company id from user prompt
    insId = run_name_interpretation_agent(user_prompt).insId
    print(insId)

    # call bd api and create df of kpis
    bd = BorsdataClient()
    kpis_json = bd.get_instrument_kpi(insId=insId)

    # convert to df
    df = kpis_json_to_df(kpis_json)

    # find the industry KPI based on instrument ID
    rel_kpis = _find_industry_kpis(insId)

    # filter df for relevant kpis
    df_subset = filter_relevant_kpis(df, rel_kpis)

    # create report for the relevant kpis
    create_kpis_report(df_subset)

    print(df_subset.head())
    print(df_subset.info())
