"""Main entry point for bd_agent application"""

1
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from bd_agent.router import run_agent


def main():
    """Main entry point. Only redirects to run_agent in router"""
    run_agent()


if __name__ == "__main__":
    main()
