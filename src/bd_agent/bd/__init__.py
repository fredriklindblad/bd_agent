"""
bd — adapters mot Börsdata API.

Publikt API:
- BorsdataClient: client to interact with Börsdata API
"""

from bd_agent.bd._client import BorsdataClient
from bd_agent.bd._models import InstrumentInfo
from bd_agent.bd.repository import get_instrument_info_by_id, kpis_json_to_df
from bd_agent.bd.metadata import (
    get_sectors,
    get_industries,
    get_companies_by_sector,
    get_companies_by_industry,
)
from bd_agent.bd._helpers import kpi_map

__all__ = [
    "BorsdataClient",
    "InstrumentInfo",
    "get_instrument_info_by_id",
    "kpis_json_to_df",
    "get_sectors",
    "get_industries",
    "get_companies_by_sector",
    "get_companies_by_industry",
    "kpi_map",
]


"""
    FL learning notes: python package import
    använd __init__.py i mappen för publikt API 
    om du kör import * så kommer alla moduler som börjar med _ (underscore) att ignoreras.
    
"""
