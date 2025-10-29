"""module is for classification metrics"""

from dataclasses import dataclass
from typing import Any
import pandas as pd


def confusion_matrix(ref: list[str], pred: list[str]) -> dict[str, dict[str, int]]:
    """Computes confusion matrix for classification task.
    References as rows, predictions as columns.
    Args:
        ref: list of reference labels
        pred: list of predicted labels
    Returns:
        confusion matrix as a nested dict
    """
    labels = sorted(set(ref) | set(pred))
    mat: dict[str, dict[str, int]] = {l: {p: 0 for p in labels} for l in labels}

    # loop over ref and pred pairs
    for r, p in zip(ref, pred):
        mat[r][p] += 1

    return mat


def accuracy(ref: list[str], pred: list[str]) -> float:
    """Computes accuracy for classification task.
    Args:
        ref: list of reference labels
        pred: list of predicted labels
    Returns:
        accuracy as float
    """
    correct = sum(1 for r, p in zip(ref, pred) if r == p)
    return correct / len(ref) if ref else 0.0


def precision(ref: list[str], pred: list[str], label: str | None = None) -> float:
    """Computes precision for individual label or overall.
    Args:
        ref: list of reference labels
        pred: list of predicted labels
        label: specific label to compute precision for (if None, computes overall precision)
    Returns:
        precision as float
    """
    labels = set(ref) | set(pred) if label is None else {label}
    precisions = []
    for l in labels:
        true_pos = sum(1 for r, p in zip(ref, pred) if r == l and p == l)
        false_pos = sum(1 for r, p in zip(ref, pred) if r != l and p == l)
        prec = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0.0
        precisions.append(prec)

    return sum(precisions) / len(precisions) if precisions else 0.0


def recall(ref: list[str], pred: list[str], label: str | None = None) -> float:
    """Computes recall for individual label or overall.
    Args:
        ref: list of reference labels
        pred: list of predicted labels
        label: specific label to compute recall for (if None, computes overall recall)
    Returns:
        recall as float
    """
    labels = set(ref) | set(pred) if label is None else {label}
    recalls = []
    for l in labels:
        true_pos = sum(1 for r, p in zip(ref, pred) if r == l and p == l)
        false_neg = sum(1 for r, p in zip(ref, pred) if r == l and p != l)
        rec = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0.0
        recalls.append(rec)

    return sum(recalls) / len(recalls) if recalls else 0.0


# create dummy test recall
refs = ["A", "B", "A", "C", "B", "A", "B"]
preds = ["A", "B", "C", "C", "B", "A", "A"]
print("Recall:", recall(refs, preds))
print("Recall for label A:", recall(refs, preds, label="A"))
print("Recall for label B:", recall(refs, preds, label="B"))
print("Recall for label C:", recall(refs, preds, label="C"))
