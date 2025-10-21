"""helpers to the analyze_agent"""

import math
import requests
import pandas as pd
import matplotlib.pyplot as plt
import bd_agent.bd as bd
from bd_agent.agents._find_industry_kpis.__find_industry_kpis import _find_industry_kpis
from bd_agent.agents._find_industry_kpis._models import KPISuggestion


def filter_relevant_kpis(df: pd.DataFrame, relKpis: KPISuggestion) -> pd.DataFrame:
    """ """
    df = df
    kpis = relKpis
    kpi_ids = [kpi.id for kpi in kpis]
    df_subset = df.loc[df["KpiId"].isin(kpi_ids)].copy()

    return df_subset


def create_kpis_report(df: pd.DataFrame, insId: int, rel_kpis: list[KPISuggestion]):
    """ """
    # sort the input df on KpiId and year
    df = df.sort_values(by=["KpiId", "y"])

    # get industry data
    industryId = bd.get_instrument_info_by_id(insId).industryId
    industry_avg_df = get_industry_average_kpis(industryId, rel_kpis)
    print(industry_avg_df.info())
    print(df.info())

    # group by KPI
    kpi_groups = list(df.groupby("KpiId"))
    num_kpis = len(kpi_groups)

    # Determine grid size
    cols = 3
    rows = math.ceil(num_kpis / cols)

    # create figure and axes
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 3))
    axes = axes.flatten()

    # loop over each unique kpi id
    for i, (kpi, group) in enumerate(kpi_groups):
        ax = axes[i]
        kpi_name = group["KpiName"].iloc[0]
        kpi_id = group["KpiId"].iloc[0]

        # plot company values
        ax.plot(
            group["y"],
            group["v"],
            marker="o",
            linestyle="-",
            color="Blue",
            label="Company",
        )

        # plot industry average
        industry_subset = industry_avg_df[industry_avg_df["KpiId"] == kpi_id]
        if not industry_subset.empty:
            ax.plot(
                industry_subset["y"],
                industry_subset["industry_avg"],
                linestyle="--",
                color="green",
                label="Industry avg",
            )

        ax.set_title(f"{kpi_name} ({kpi_id})", fontsize=10)
        ax.set_xlabel("Year")
        ax.set_ylabel("Value")
        ax.grid(True)
        ax.legend(fontsize=8)

    # return plot
    plt.tight_layout()
    return fig
    # plt.show()


# -------- internal functions --------
def get_industry_average_kpis(
    industryId, rel_kpis: list[KPISuggestion], report_type="year", price_type="mean"
) -> pd.DataFrame:
    """Takes industryId and kpiList as argument and returns a df: [year,insId, kpiId, value] with averages per year"""

    # get a list of companyId for industry and a list for kpiId for industry
    # compList = [ins["insId"] for ins in bd.get_companies_by_industry(industryId)]
    compList = [i for i in range(0, 130)]
    kpiList = [kpi.id for kpi in rel_kpis]

    # create bd client
    client = bd.BorsdataClient()

    # loop companies in chunks over kpis and return a df
    rows = []
    for kpi_id in kpiList:
        for chunk in chunk_list(compList, 50):
            # print(f"{kpi_id}:NEW CHUNK------------------")
            # print(chunk)
            url = f"{client.base_url}/Instruments/kpis/{kpi_id}/{report_type}/{price_type}/history"
            params = {"authKey": client.api_key, "instList": ",".join(map(str, chunk))}
            response = requests.get(url, params=params, timeout=60)
            data = response.json()
            # print("DATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            # print(data)
            # print(type(data))

            for item in data.get("kpisList", []):
                ins = item["instrument"]
                for v in item.get("values", []):
                    val = v.get("v")
                    if val is not None:
                        rows.append(
                            {
                                "y": v["y"],
                                "insId": ins,
                                "KpiId": kpi_id,
                                "value": float(val),
                            }
                        )
    df = pd.DataFrame(rows)

    # use industry data in df to create industry average df
    industry_avg = (
        df.groupby(["KpiId", "y"], as_index=False)["value"]
        .mean()
        .rename(columns={"value": "industry_avg"})
    )

    return industry_avg


def chunk_list(lst, size=50):
    """Chunks a list into several lists"""
    for i in range(0, len(lst), size):
        yield lst[i : i + size]
