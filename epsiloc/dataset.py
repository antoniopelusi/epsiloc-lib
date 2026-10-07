import json
import csv
from pathlib import Path


def _validate(metadata):
    if not isinstance(metadata, list):
        raise ValueError("Metadata must be a JSON array.")

    for i, col in enumerate(metadata):
        if not isinstance(col, dict):
            raise ValueError(f"Column {i}: must be an object.")

        col_type = col.get("type")
        if col_type not in ("continuous", "discrete", "categorical"):
            raise ValueError(f"Column {i}: invalid type {col_type!r}.")

        epsilon = col.get("epsilon")
        if not isinstance(epsilon, (int, float)) or epsilon <= 0:
            raise ValueError(f"Column {i}: epsilon must be a positive number.")

        if col_type in ("continuous", "discrete"):
            mn, mx = col.get("min"), col.get("max")
            if mn is None or mx is None:
                raise ValueError(f"Column {i}: min and max are required.")
            if not isinstance(mn, (int, float)) or not isinstance(mx, (int, float)):
                raise ValueError(f"Column {i}: min and max must be numbers.")
            if mx <= mn:
                raise ValueError(f"Column {i}: max must be strictly greater than min.")
            if col_type == "continuous":
                dp = col.get("decimal_places")
                if not isinstance(dp, int) or dp < 0:
                    raise ValueError(f"Column {i}: decimal_places must be a non-negative integer.")

        elif col_type == "categorical":
            cats = col.get("categories")
            if not isinstance(cats, list) or len(cats) < 2:
                raise ValueError(f"Column {i}: categories must be a list with at least 2 elements.")


def load(base_path):
    data_path = Path(base_path)
    metadata_path = data_path.with_suffix(".json")

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    _validate(metadata)

    converters = {"continuous": float, "discrete": int, "categorical": str}
    conv = [converters[col["type"]] for col in metadata]

    with open(data_path, "r", encoding="utf-8") as f:
        rows = []
        for i, row in enumerate(csv.reader(f)):
            if len(row) != len(conv):
                raise ValueError(f"Row {i}: expected {len(conv)} columns, got {len(row)}.")
            rows.append([c(v) for c, v in zip(conv, row)])

    return metadata, rows


def save(data, base_path):
    src = Path(base_path).with_suffix(".csv")
    dst = src.with_name(src.stem + "_privatized.csv")
    with open(dst, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(data)
