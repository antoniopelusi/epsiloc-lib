import json
import csv
from pathlib import Path
from typing import Any

def _validate_metadata(metadata: list[dict]) -> None:
    if not isinstance(metadata, list):
        raise ValueError("Metadata JSON must be a list of dictionaries")

    for i, col_meta in enumerate(metadata):
        if not isinstance(col_meta, dict):
            raise ValueError(f"Metadata entry {i} must be a dictionary")

        col_type = col_meta.get("type")
        if col_type not in ["continuous", "discrete", "categorical"]:
            raise ValueError(f"Invalid type in column {i}: {col_type}")

        epsilon = col_meta.get("epsilon")
        if not isinstance(epsilon, (float)) or epsilon <= 0:
            raise ValueError(f"Invalid epsilon in column {i}: {epsilon}")

        if col_type in ["continuous", "discrete"]:
            if "min" not in col_meta or "max" not in col_meta:
                raise ValueError(f"Columns of type {col_type} require 'min' and 'max' (column {i})")
            if not isinstance(col_meta.get("rejection_sampling"), bool):
                raise ValueError(f"'rejection_sampling' must be boolean in column {i}")
            if col_type == "continuous":
                if "decimal_places" not in col_meta:
                    raise ValueError(f"'decimal_places' is required for continuous columns (column {i})")
                if not isinstance(col_meta["decimal_places"], int) or col_meta["decimal_places"] < 0:
                    raise ValueError(f"Invalid 'decimal_places' in column {i}: {col_meta['decimal_places']}")

        elif col_type == "categorical":
            if "categories" not in col_meta:
                raise ValueError(f"'categories' is required for categorical columns (column {i})")
            if not isinstance(col_meta["categories"], list) or len(col_meta["categories"]) < 2:
                raise ValueError(f"'categories' must be a list of length >= 2 in column {i}")

def fetch_dataset(base_path: str) -> tuple[list[dict], list[list[Any]]]:
    data_path = Path(base_path)
    metadata_path = data_path.with_suffix(".json")

    if not metadata_path.exists():
        raise FileNotFoundError(f"{metadata_path} does not exist")
    if not data_path.exists():
        raise FileNotFoundError(f"{data_path} does not exist")

    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        _validate_metadata(metadata)

    converters = []
    for col_meta in metadata:
        data_type = col_meta.pop("type").lower()  # remove 'type' after use
        type_map = {"continuous": float, "discrete": int, "categorical": str}
        converters.append(type_map[data_type])

    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = []
        for row_index, row in enumerate(reader):
            if len(row) != len(converters):
                raise ValueError(
                    f"Row {row_index} in CSV has {len(row)} columns, but metadata defines {len(converters)} columns"
                )
            converted_row = [converter(value) for converter, value in zip(converters, row)]
            data.append(converted_row)

    return metadata, data
