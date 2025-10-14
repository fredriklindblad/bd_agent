"""certain meta data api calls"""

import requests

from bd_agent.bd import BorsdataClient


def get_sectors() -> dict:
    """Returns a dict of sectorId:sectorName from BD API"""
    client = BorsdataClient()
    url = f"{client.base_url}/sectors?authKey={client.api_key}"
    response = requests.get(url)
    sectors_raw_dict = response.json()["sectors"]
    sectors_dict = {s["id"]: s["name"] for s in sectors_raw_dict}
    return sectors_dict


def get_branch() -> dict:
    """Returns a dict of branchId:branchName from BD API"""
    client = BorsdataClient()
    url = f"{client.base_url}/branches?authKey={client.api_key}"
    response = requests.get(url)
    branches_raw_dict = response.json()["branches"]
    branches_dict = {b["id"]: b["name"] for b in branches_raw_dict}
    return branches_dict
