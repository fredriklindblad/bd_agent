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
