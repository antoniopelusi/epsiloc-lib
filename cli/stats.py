import csv
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import math

def _load_csv(path: Path) -> list[list[str]]:
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        return [row for row in reader]

def _load_json(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def stats(base_path: str) -> None:
    base = Path(base_path)
    data_path = base.with_suffix(".csv")
    private_path = data_path.with_name(data_path.stem + "_privatized.csv")
    metadata_path = base.with_suffix(".json")

    if not data_path.exists():
        raise FileNotFoundError(f"{data_path} does not exist")
    if not private_path.exists():
        raise FileNotFoundError(f"{private_path} does not exist")
    if not metadata_path.exists():
        raise FileNotFoundError(f"{metadata_path} does not exist")

    data = np.array(_load_csv(data_path), dtype=object)
    data_private = np.array(_load_csv(private_path), dtype=object)
    metadata = _load_json(metadata_path)

    num_cols = data.shape[1]
    ncols = min(3, num_cols)
    nrows = math.ceil(num_cols / ncols)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(5*ncols, 4*nrows))
    axes = np.atleast_1d(axes).ravel()

    for col in range(num_cols):
        ax = axes[col]
        col_data = data[:, col]
        col_private = data_private[:, col]
        col_meta = metadata[col]
        col_type = col_meta["type"]

        if col_type == "continuous":
            col_data = col_data.astype(float)
            col_private = col_private.astype(float)
            min_val = min(col_data.min(), col_private.min())
            max_val = max(col_data.max(), col_private.max())
            desired_width = 0.1
            num_bins = max(1, int((max_val - min_val) / desired_width))
            bins = np.linspace(min_val, max_val, num_bins + 1)
            ax.hist(col_data, bins=bins, density=True, alpha=0.5, label="Original", color="tab:blue")
            ax.hist(col_private, bins=bins, density=True, alpha=0.5, label="Privatized", color="tab:orange")
            ax.set_title(f"Column {col+1} (continuous)")
            ax.set_xlabel("Value")
            ax.set_ylabel("Density")

        elif col_type == "discrete":
            col_data = col_data.astype(int)
            col_private = col_private.astype(int)
            min_val = min(col_data.min(), col_private.min())
            max_val = max(col_data.max(), col_private.max())
            bins = np.arange(min_val - 0.5, max_val + 1.5, 1)
            ax.hist(col_data, bins=bins, alpha=0.5, label="Original", color="tab:blue")
            ax.hist(col_private, bins=bins, alpha=0.5, label="Privatized", color="tab:orange")
            ax.set_xticks(np.arange(min_val, max_val + 1))
            ax.set_title(f"Column {col+1} (discrete)")
            ax.set_xlabel("Value")
            ax.set_ylabel("Count")

        elif col_type == "categorical":
            categories = sorted(set(col_data) | set(col_private))
            mapping = {cat: idx for idx, cat in enumerate(categories)}
            col_data_idx = np.array([mapping[x] for x in col_data])
            col_private_idx = np.array([mapping[x] for x in col_private])
            bins = np.arange(-0.5, len(categories) + 0.5, 1)
            ax.hist(col_data_idx, bins=bins, alpha=0.5, label="Original", color="tab:blue")
            ax.hist(col_private_idx, bins=bins, alpha=0.5, label="Privatized", color="tab:orange")
            ax.set_xticks(range(len(categories)))
            ax.set_xticklabels(categories, rotation=45, ha="right")
            ax.set_title(f"Column {col+1} (categorical)")
            ax.set_ylabel("Count")

        ax.legend()

    for k in range(num_cols, len(axes)):
        fig.delaxes(axes[k])

    fig.suptitle(f"Original vs Privatized distributions for {base.stem}", fontsize=14)
    plt.tight_layout()
    plt.show()
