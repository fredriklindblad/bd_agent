"""Module is eval of intents classifier"""

import pandas as pd

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bd_agent.eval.io import load_default_intents, run_dir, write_json
from bd_agent.intents.classifier import IntentClassification, intent_classifier
from bd_agent.eval.metrics.classification import confusion_matrix, accuracy, precision


@dataclass
class IntentEvalRow:
    """
    Represents a single evaluation example for intent classification.

    Attributes:
        user_prompt: The raw user input sent to the agent.
        gold_intent: The correct, expected intent label from the golden set.
        pred_intent: The predicted intent label from the classifier.
        confidence: Model confidence score for the prediction (0–1).
        meta: Additional metadata (e.g., language, difficulty, source).
    """

    input: str
    expected: str
    predicted: str
    confidence: float
    meta: dict[str, Any]


def _predict(prompt: str) -> IntentClassification:
    """Gets intent prediction from the classifier
    Returns IntentClassification object with .intent, .confidence, .reasoning"""
    out = intent_classifier(prompt)
    return out


def _build_predictions(rows: list[dict]) -> list[IntentEvalRow]:
    """Builds predictions for a list of reference rows.
    Each row is a dict with keys: "input", "expected", "meta"
    Returns a list of IntentEvalRow objects:
    - input: user prompt
    - expected: expected intent
    - predicted: predicted intent
    - confidence: model confidence
    - meta: additional metadata in {}
    """
    preds: list[IntentEvalRow] = []
    for r in rows:
        out = _predict(r["input"])
        preds.append(
            IntentEvalRow(
                input=r["input"],
                expected=r["expected"],
                predicted=out.intent,
                confidence=out.confidence,
                meta=r.get("meta", {}),
            )
        )
    return preds


def create_report(preds: list[IntentEvalRow]) -> dict[str, Any]:
    """Creates a report with below metrics.

    Overall metrics:
        accuracy,
        macro precision,
        macro recall,
        macro F1-score,
        weighted F1-score,
        confusion matrix
        coverage-accuracy curve

    Per-intent metrics:
        support,
        accuracy,
        precision,
        recall,
        F1-score,
        confidence mean

    """

    # ------ CONFUSION MATRIX ------
    # extract ref and pred for confusion matrix
    ref = [r.expected for r in preds]
    pred = [r.predicted for r in preds]

    # create confusion matrix
    cm = confusion_matrix(ref, pred)

    # calculate other overall metrics here (accuracy, F1, etc.) - TODO
    acc = accuracy(ref, pred)
    macro_precision = precision(ref, pred)

    # ------ CREATE REPORT DICTIONARY ------
    report: dict[str, Any] = {
        "meta": {"num_samples": len(preds), "labels": list(cm.keys())},
        "overall": {
            "confusion_matrix": cm,
            "accuracy": acc,
            "precision": macro_precision,
            # TODO add other overall metrics
        },
    }

    return report


def run() -> Path:
    """Runs intents eval and returns path to results file"""
    rows = load_default_intents()  # TODO limit is for testing
    preds = _build_predictions(rows)  # returns a list of IntentEvalRow

    # create report
    report = create_report(preds)  # TODO implement

    # create output directory
    outdir = run_dir(label="intents-eval")
    out_path = outdir / "intent_report.json"

    # write report to json file
    write_json(out_path, report)  # TODO implement

    return out_path
