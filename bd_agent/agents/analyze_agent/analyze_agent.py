# analyze_agent/analyze_agent.py
from __future__ import annotations

from bd_agent.agents._name_interpretation_agent.name_interpretation_agent import (
    run as run_name_interpretation_agent,
)
from bd_agent.bd import BorsdataClient, kpis_json_to_df


def run(user_prompt: str):
    """ """
    # interpret company id from user prompt
    insId = run_name_interpretation_agent(user_prompt).insId

    # call bd api and create df of kpis
    bd = BorsdataClient()
    kpis_json = bd.get_instrument_kpi(insId=insId)
    df = kpis_json_to_df(kpis_json)

    print(df.info())
