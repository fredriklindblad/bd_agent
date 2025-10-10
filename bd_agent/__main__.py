# Main entry point for bd_agent application

from dotenv import load_dotenv, find_dotenv
from bd_agent.router import router

from bd_agent.bd import BorsdataClient, get_instrument_info_by_id  # temp import

load_dotenv(find_dotenv())


def main():
    # router()

    # bd = BorsdataClient()
    # print(bd.get_nordic_instruments())
    # print(type(bd.get_nordic_instruments()))
    # print(bd.get_nordic_instruments()["instruments"][0])  # Example access to data

    ins = get_instrument_info_by_id(2591)
    print(type(ins))
    print(ins)


if __name__ == "__main__":
    main()
