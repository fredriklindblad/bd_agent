"""I/O for evaluation data"""

import json
import uuid
from pathlib import Path, WindowsPath
from importlib import resources as ir
from typing import Iterable
from datetime import datetime


# ---- Errors ----
class EvalDataError(RuntimeError):
    pass


# ---- Package Resources ----
def _golden_intents_path() -> WindowsPath:
    """Returns the path to the golden intents file
    bd_agent/eval/reference_sets/golden_intents.jsonl"""
    base = ir.files("bd_agent.eval")
    return Path(base.joinpath("reference_sets", "golden_intents.jsonl"))


def load_default_intents() -> list[dict]:
    """Loads the golden set"""
    res = _golden_intents_path()
    if not res.exists():
        raise EvalDataError(
            "Packaged golden set missing. Ensure pacakge-data is included."
        )
    with res.open("r", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    if not rows:
        raise EvalDataError("Golden set it empty.")
    return rows


# ---- Artifacts Handling ----
def _artifacts_dir() -> Path:
    """Returns the path to the artifacts directory
    bd_agent/eval/artifacts/"""
    base = ir.files("bd_agent.eval")
    return Path(base.joinpath("artifacts"))


def run_dir(root: Path | None, label: str = "intents-eval") -> Path:
    """Create a timestamped, uniques directory for one eval run"""
    root = root or _artifacts_dir()
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    rid = uuid.uuid4().hex[:8]
    d = root / f"{label}-{stamp}-{rid}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_jsonl(path: Path, rows: Iterable[dict]):
    """Writes to jsonl. Used for eval results."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for obj in rows:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
