"""Module is eval of intents classifier"""

import json
import os
from pathlib import Path, WindowsPath
from importlib import resources as ir
from typing import Iterable


# --- Artifacts location ----
def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_artifacts_dir() -> Path:
    """Returns the artifacts directory"""
    root = _project_root()
    print(type(root / "bd_agent" / "eval" / "artifacts"))
    print(root / "bd_agent" / "eval" / "artifacts")
    return root / "bd_agent" / "eval" / "artifacts"


def ensure_artifacts_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


# ---- Errors ----
class EvalDataError(RuntimeError):
    pass


# ---- Resources ----
def _intents_resource() -> WindowsPath:
    """Returns a Traversable to bd_agent/eval/reference_sets/golden_intents.jsonl inside package"""
    base = ir.files("bd_agent.eval")
    return base.joinpath("reference_sets", "golden_intents.jsonl")


def write_jsonl(path: Path, rows: Iterable[dict]):
    """Writes to jsonl. Used for eval results."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for obj in rows:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_default_intents() -> list[dict]:
    """Loads the golden set"""
    res = _intents_resource()
    if not res.exists():
        raise EvalDataError(
            "Packaged golden set missing. Ensure pacakge-data is included."
        )
    with res.open("r", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    if not rows:
        raise EvalDataError("Golden set it empty.")
    return rows


# TODO delete TESTONLY
def run_intents_eval():
    data = load_default_intents()
    out_path = ensure_artifacts_dir(get_artifacts_dir()) / "probe.jsonl"
    write_jsonl(out_path, data[:2])
