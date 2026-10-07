# epsiloc

A command-line tool for applying **local differential privacy (LDP)** to tabular CSV datasets.

Each value is perturbed independently using a provably private mechanism before the data leaves the owner's machine.

---

## How it works

Epsiloc applies one of three mechanisms to each column, based on the type declared in the metadata JSON:

| Column type | Mechanism | Privacy guarantee |
|---|---|---|
| `discrete` (integer) | Discrete Laplace (two-sided Geometric) | ε-LDP |
| `continuous` (float) | Laplace | ε-LDP |
| `categorical` (string) | k-ary Randomized Response | ε-LDP |

**Sensitivity** for numeric columns is `max - min`, the correct L1 sensitivity for a single scalar value under local DP.

**Bounded output** is achieved by clamping the noisy value to `[min, max]` after drawing from the full distribution. Clamping is post-processing and does not weaken the ε-DP guarantee. Rejection sampling is avoided because it produces a truncated distribution that breaks the standard ε-DP proof.

**Epsilon (ε)** is set per column. Smaller ε means more noise and stronger privacy. The total privacy cost for a full row is the sum of all column epsilons (sequential composition).

---

## Setup

Requires **Python 3.9+**.

```bash
make setup
```

---

## Usage

```bash
python3 epsiloc.py <dataset.csv> [--privatize] [--metadata] [--stats]
```

Or via make (defaults to `test_dataset/iris.csv`):

```bash
make privatize   # apply noise, writes dataset_privatized.csv
make stats       # plot original vs privatized distributions
make metadata    # interactively create a metadata JSON
```

### `--privatize`

Applies noise to every value and writes `<dataset>_privatized.csv` next to the original.

### `--metadata`

Interactively prompts for type, epsilon, and bounds/categories for each column, then writes `<dataset>.json`.

### `--stats`

Plots side-by-side histograms of original vs. privatized distributions for each column. Requires `--privatize` to have been run first.

---

## Metadata format

The metadata JSON is a list of column descriptors in CSV column order.

**Discrete** (integer):
```json
{ "type": "discrete", "epsilon": 1.0, "min": 0, "max": 100 }
```

**Continuous** (float):
```json
{ "type": "continuous", "epsilon": 1.0, "min": 0.0, "max": 1.0, "decimal_places": 2 }
```

**Categorical** (string):
```json
{ "type": "categorical", "epsilon": 1.0, "categories": ["a", "b", "c"] }
```

`test_dataset/iris.json` is a ready-to-use example.

---

## Project structure

```
epsiloc.py              # entry point — privatize, metadata, stats
epsiloc/
  mechanisms.py         # Laplace, Discrete Laplace, k-RR
  dataset.py            # load (CSV + metadata) and save
test_dataset/
  iris.csv              # Iris dataset (150 rows)
  iris.json             # pre-configured metadata (ε = 1.0 per column)
```
