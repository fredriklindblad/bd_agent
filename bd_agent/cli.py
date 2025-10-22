"""CLI interface for bd_agent"""

from bd_agent.router import run_agent
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def run_cli() -> None:
    """Run agent in CLI mode"""
    result = run_agent(input("What can I help you with today?\n>>> "))
    if isinstance(result, Figure):
        plt.figure(result)
        plt.show()
