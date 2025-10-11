"""Creates the BorsdataClient class that is the connection to Börsdata"""

from __future__ import annotations
import os
from typing import Optional

import requests


BASE_URL = "https://apiservice.borsdata.se/v1"


class BorsdataClient:
    """Client for Borsdata API v1"""

    def __init__(self, api_key: Optional[str] = None, base_url: str = BASE_URL) -> None:
        """Initializes the BorsdataClient with an API key and base URL."""
        self.api_key = api_key or os.getenv("BORSDATA_API_KEY")
        self.base_url = base_url

    def get_nordic_instruments(self) -> dict:
        """Returns a JSON with info about all nordic instruments from BD API call"""
        url = f"{self.base_url}/instruments?authKey={self.api_key}"
        response = requests.get(url)
        data = response.json()
        return data

    def get_instrument_kpi(self, insId=1, reportType="year") -> dict:
        """Returns a JSON with KPI info for a specific instrument from BD API call"""
        url = f"{self.base_url}/instruments/{insId}/kpis/{reportType}/summary?authKey={self.api_key}"
        response = requests.get(url)
        data = response.json()
        return data
