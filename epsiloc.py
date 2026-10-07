import argparse
import csv
import json
import sys
from pathlib import Path

from epsiloc.dataset import load, save
from epsiloc.mechanisms import laplace, discrete_laplace, k_randomized_response


def privatize(dataset_path):
    metadata, data = load(dataset_path)
    result = []
    for row in data:
        out = []
        for value, col in zip(row, metadata):
            t = col["type"]
            if t == "discrete":
                out.append(discrete_laplace(int(value), col["epsilon"], col["min"], col["max"]))
            elif t == "continuous":
                out.append(laplace(float(value), col["epsilon"], col["min"], col["max"], col["decimal_places"]))
            elif t == "categorical":
                out.append(k_randomized_response(str(value), col["epsilon"], col["categories"]))
            else:
                raise ValueError(f"Unknown column type: {t!r}")
        result.append(out)
    save(result, dataset_path)


def create_metadata(csv_path):
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"{csv_path} does not exist")

    with open(path, "r", encoding="utf-8") as f:
        num_columns = len(next(csv.reader(f)))

    metadata = []
    for i in range(num_columns):
        print(f"\nColumn {i + 1}/{num_columns}:")

        while True:
            col_type = input("  Type (discrete, continuous, categorical): ").strip().lower()
            if col_type in ("discrete", "continuous", "categorical"):
                break
            print("  Invalid type.")

        while True:
            try:
                epsilon = float(input("  Epsilon (> 0): ").strip())
                if epsilon > 0:
                    break
                print("  Epsilon must be > 0.")
            except ValueError:
                print("  Enter a number.")

        col = {"type": col_type, "epsilon": epsilon}

        if col_type in ("discrete", "continuous"):
            while True:
                try:
                    mn = float(input("  Min: ").strip())
                    mx = float(input("  Max: ").strip())
                    if mx > mn:
                        break
                    print("  Max must be strictly greater than min.")
                except ValueError:
                    print("  Enter numbers.")
            col.update({"min": mn, "max": mx})

        if col_type == "continuous":
            while True:
                try:
                    dp = int(input("  Decimal places (>= 0): ").strip())
                    if dp >= 0:
                        break
                    print("  Must be >= 0.")
                except ValueError:
                    print("  Enter an integer.")
            col["decimal_places"] = dp

        if col_type == "categorical":
            while True:
                cats = [c.strip() for c in input("  Categories (comma-separated, >= 2): ").strip().split(",") if c.strip()]
                if len(cats) >= 2:
                    break
                print("  At least 2 categories required.")
            col["categories"] = cats

        metadata.append(col)

    out_path = path.with_suffix(".json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
    print(f"Metadata saved to {out_path}")


def stats(base_path):
    import matplotlib.pyplot as plt
    import numpy as np

    base = Path(base_path)
    private_path = base.with_name(base.stem + "_privatized.csv")

    if not private_path.exists():
        raise FileNotFoundError(f"Privatized dataset not found: {private_path}")

    metadata, orig_rows = load(base_path)

    converters = {"continuous": float, "discrete": int, "categorical": str}
    conv = [converters[col["type"]] for col in metadata]
    with open(private_path, "r", encoding="utf-8") as f:
        priv_rows = [[c(v) for c, v in zip(conv, row)] for row in csv.reader(f)]

    orig = np.array(orig_rows, dtype=object)
    priv = np.array(priv_rows, dtype=object)

    num_cols = orig.shape[1]
    ncols = min(3, num_cols)
    nrows = -(-num_cols // ncols)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(5 * ncols, 4 * nrows))
    axes = np.atleast_1d(axes).ravel()

    for col in range(num_cols):
        ax = axes[col]
        o = orig[:, col]
        p = priv[:, col]
        col_type = metadata[col]["type"]

        if col_type == "continuous":
            o, p = o.astype(float), p.astype(float)
            lo, hi = min(o.min(), p.min()), max(o.max(), p.max())
            bins = np.linspace(lo, hi, max(1, int((hi - lo) / 0.1)) + 1)
            ax.hist(o, bins=bins, density=True, alpha=0.5, label="Original", color="tab:blue")
            ax.hist(p, bins=bins, density=True, alpha=0.5, label="Privatized", color="tab:orange")
            ax.set_ylabel("Density")

        elif col_type == "discrete":
            o, p = o.astype(int), p.astype(int)
            lo, hi = min(o.min(), p.min()), max(o.max(), p.max())
            bins = np.arange(lo - 0.5, hi + 1.5, 1)
            ax.hist(o, bins=bins, alpha=0.5, label="Original", color="tab:blue")
            ax.hist(p, bins=bins, alpha=0.5, label="Privatized", color="tab:orange")
            ax.set_xticks(np.arange(lo, hi + 1))
            ax.set_ylabel("Count")

        elif col_type == "categorical":
            cats = sorted(set(o) | set(p))
            mapping = {c: i for i, c in enumerate(cats)}
            o_idx = np.array([mapping[x] for x in o])
            p_idx = np.array([mapping[x] for x in p])
            bins = np.arange(-0.5, len(cats) + 0.5, 1)
            ax.hist(o_idx, bins=bins, alpha=0.5, label="Original", color="tab:blue")
            ax.hist(p_idx, bins=bins, alpha=0.5, label="Privatized", color="tab:orange")
            ax.set_xticks(range(len(cats)))
            ax.set_xticklabels(cats, rotation=45, ha="right")
            ax.set_ylabel("Count")

        ax.set_title(f"Column {col + 1} ({col_type})")
        ax.set_xlabel("Value")
        ax.legend()

    for k in range(num_cols, len(axes)):
        fig.delaxes(axes[k])

    fig.suptitle(f"Original vs Privatized — {base.stem}", fontsize=14)
    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="epsiloc — local differential privacy toolkit")
    parser.add_argument("dataset", help="Path to the dataset (.csv)")
    parser.add_argument("--privatize", action="store_true", help="Privatize the dataset")
    parser.add_argument("--metadata", action="store_true", help="Create metadata JSON interactively")
    parser.add_argument("--stats", action="store_true", help="Compare original vs privatized distributions")

    args = parser.parse_args()

    if not (args.privatize or args.metadata or args.stats):
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.metadata:
        create_metadata(args.dataset)
    if args.privatize:
        privatize(args.dataset)
        print("|> Privatized dataset generated.")
    if args.stats:
        stats(args.dataset)


if __name__ == "__main__":
    main()
