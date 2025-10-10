"""repository.py consists of functions to interact with the data from api client"""

from bd_agent.bd import BorsdataClient, InstrumentInfo


def get_instrument_info_by_id(ins_id: int) -> InstrumentInfo:
    """Fetches instrument information by its ID and returns an Instrument object."""
    data = BorsdataClient().get_nordic_instruments()
    for item in data.get("instruments"):
        if item["insId"] == ins_id:
            return InstrumentInfo(**item)
    return None
