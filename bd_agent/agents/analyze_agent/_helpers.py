"""helpers to the analyze_agent"""

import math
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


def create_kpis_report(df: pd.DataFrame):
    """ """
    # sort the input df on KpiId and year
    df = df.sort_values(by=["KpiId", "y"])

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

        # plot axes
        ax.plot(group["y"], group["v"], marker="o", linestyle="-", label=kpi_name)
        ax.set_title(f"{kpi_name} ({kpi_id})", fontsize=10)
        ax.set_xlabel("Year")
        ax.set_ylabel("Value")
        ax.grid(True)
        ax.legend(fontsize=8)

    # show plot
    plt.tight_layout()
    plt.show()


# -------- internal functions --------
def get_branch_average_kpis(branchId):
    """ """
    pass
