"""repository.py consists of functions to interact with the data from api client"""

from ._client import BorsdataClient
from ._models import InstrumentInfo
from ._helpers import kpi_map
import pandas as pd


def get_instrument_info_by_id(ins_id: int) -> InstrumentInfo:
    """Fetches instrument information by its ID and returns an Instrument object."""
    data = BorsdataClient().get_nordic_instruments()
    print("DATA", data[0])
    for item in data:
        if item["insId"] == ins_id:
            return InstrumentInfo(**item)
    return None


def kpis_json_to_df(json: dict) -> pd.DataFrame:
    """converts the raw json from kpi:s api call to a pandas dataframe"""
    values_list = json["kpis"]

    # convert to list of rows
    rows = []
    for kpi in values_list:
        kpi_id = kpi["KpiId"]
        for val in kpi["values"]:
            val["KpiId"] = kpi_id
            rows.append(val)

    # convert to df
    df = pd.DataFrame(rows)

    # add KpiName as col in df
    df["KpiName"] = df["KpiId"].map(kpi_map)

    return df
