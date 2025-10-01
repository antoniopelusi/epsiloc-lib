import argparse
import sys
import numpy as np
from cli.metadata import create_metadata
from cli.stats import stats
from epsiloc.privatize import privatize

# np.random.seed(42)

def main():
    parser = argparse.ArgumentParser(
        description="Epsiloc - Differential Privacy Toolkit"
    )
    parser.add_argument(
        "dataset",
        type=str,
        help="Path to the dataset (.csv)"
    )
    parser.add_argument(
        "--metadata",
        action="store_true",
        help="Create metadata JSON for the dataset"
    )
    parser.add_argument(
        "--privatize",
        action="store_true",
        help="Generate a differentially private dataset"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show comparison stats between original and private datasets"
    )

    args = parser.parse_args()

    if not (args.metadata or args.privatize or args.stats):
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.metadata:
        create_metadata(args.dataset)
        print("|> Metadata generated.")
    if args.privatize:
        privatize(args.dataset)
        print("|> Privatized dataset generated.")
    if args.stats:
        stats(args.dataset)
        print("|> Stats generated.")

if __name__ == "__main__":
    main()
