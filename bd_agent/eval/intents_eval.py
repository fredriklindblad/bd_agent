"""Module is eval of intents classifier"""

import json

from pathlib import Path

# constans for jsonl path and artifacts direction
JSONL_PATH = Path("eval/cases/intents.json")
ARTIFACTS_DIR = Path("eval/artifacts")


# read golden set i jsonl
def read_jsonl(path: Path) -> list[dict]:
    """reads jsonl and returns a list of all rows as dicts.
    I.e. jsonl -> Python Dict reader"""

    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    print(rows)
    return rows


read_jsonl(JSONL_PATH)
