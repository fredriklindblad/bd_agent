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


def f1_score(ref: list[str], pred: list[str], label: str | None = None) -> float:
    """Computes F1 score for individual label or overall.
    Args:
        ref: list of reference labels
        pred: list of predicted labels
        label: specific label to compute F1 for (if None, computes overall F1)
    Returns:
        F1 score as float
    """
    # single label
    if label is not None:
        prec = precision(ref, pred, label)
        rec = recall(ref, pred, label)
        return 0.00 if prec + rec == 0 else 2 * (prec * rec) / (prec + rec)

    # overall
    labels = sorted(set(ref) | set(pred))
    f1s = []
    for l in labels:
        prec = precision(ref, pred, l)
        rec = recall(ref, pred, l)
        f1 = 0.0 if prec + rec == 0 else 2 * (prec * rec) / (prec + rec)
        f1s.append(f1)

    return sum(f1s) / len(f1s) if f1s else 0.0


def weighted_f1_score(ref: list[str], pred: list[str]) -> float:
    """Computes weighted F1 score for classification task.
    Args:
        ref: list of reference labels
        pred: list of predicted labels
    Returns:
        weighted F1 score as float
    """
    labels = sorted(set(ref) | set(pred))
    label_counts = {l: ref.count(l) for l in labels}
    total_count = len(ref)

    weighted_f1s = []
    for l in labels:
        prec = precision(ref, pred, l)
        rec = recall(ref, pred, l)
        f1 = 0.0 if prec + rec == 0 else 2 * (prec * rec) / (prec + rec)
        weight = label_counts[l] / total_count if total_count > 0 else 0.0
        weighted_f1s.append(f1 * weight)

    return sum(weighted_f1s)


def coverage_accuracy_curve(
    ref: list[str], pred: list[tuple[str, float]]
) -> pd.DataFrame:
    """Computes coverage-accuracy curve for classification task.
    Args:
        ref: list of reference labels
        pred: list of tuples (predicted label, confidence score)
    Returns:
        coverage-accuracy curve as pandas DataFrame
    """
    #
    data = list(zip(ref, pred))
    data.sort(key=lambda x: x[1][1], reverse=True)
    total = len(data)
    correct = 0
    coverages, accuracies = [], []

    for k, (y_true, (y_pred, conf)) in enumerate(data, start=1):
        if y_true == y_pred:
            correct += 1
        coverages.append(k / total)
        accuracies.append(correct / k)

    return pd.DataFrame({"coverage": coverages, "accuracy": accuracies})
