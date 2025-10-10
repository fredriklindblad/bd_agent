"""
bd — adapters mot Börsdata API.

Publikt API:
- BorsdataClient: client to interact with Börsdata API
"""

from bd_agent.bd._client import BorsdataClient
from bd_agent.bd.models import Instrument
from bd_agent.bd.repository import get_instrument_info_by_id

__all__ = ["BorsdataClient", "Instrument", "get_instrument_info_by_id"]


"""
    FL learning notes: python package import
    använd __init__.py i mappen för publikt API 
    om du kör import * så kommer alla moduler som börjar med _ (underscore) att ignoreras.
    
"""
