"""
Main entry point for bd_agent.

Usage:
  python -m bd_agent ui
  python -m bd_agent cli
"""

# load dotenv to get api keys
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import argparse
import subprocess
from pathlib import Path


def main():
    """Main entry point with subcommands"""
    parser = argparse.ArgumentParser(description="BD Agent - Investment Analysis Bot")
    parser.add_argument(
        "mode",
        nargs="?",
        default="ui",
        choices=["ui", "cli"],
        help="Run mode: 'ui' for Streamlit interface, 'cli' for command line",
    )

    args = parser.parse_args()

    if args.mode == "ui":
        project_root = Path(__file__).parent.parent
        ui_path = Path(__file__).parent / "ui.py"
        subprocess.run(["streamlit", "run", str(ui_path)], cwd=str(project_root))
    else:
        from bd_agent.cli import run_cli

        run_cli()


if __name__ == "__main__":
    main()
