from pathlib import Path
import csv
import json

def create_metadata(csv_path: str) -> None:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"{csv_path} does not exist")

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        first_row = next(reader)
        num_columns = len(first_row)

    metadata = []

    for i in range(num_columns):
        print(f"\nColumn {i+1}/{num_columns}:")

        while True:
            col_type = input("Enter type (discrete, continuous, categorical): ").strip().lower()
            if col_type in ["discrete", "continuous", "categorical"]:
                break
            print("Invalid type. Try again.")

        while True:
            try:
                epsilon = float(input("Enter epsilon (>0): ").strip())
                if epsilon > 0:
                    break
                else:
                    print("Epsilon must be >0")
            except ValueError:
                print("Enter a numeric value")

        col_meta = {"type": col_type, "epsilon": epsilon}

        if col_type in ["discrete", "continuous"]:
            while True:
                try:
                    min_val = float(input("Enter min value: ").strip())
                    max_val = float(input("Enter max value: ").strip())
                    if max_val >= min_val:
                        break
                    else:
                        print("max must be >= min")
                except ValueError:
                    print("Enter numeric values")
            while True:
                rs_input = input("Use rejection sampling? (y/n): ").strip().lower()
                if rs_input in ["y", "n"]:
                    rejection_sampling = rs_input == "y"
                    break
            col_meta.update({"min": min_val, "max": max_val, "rejection_sampling": rejection_sampling})

        if col_type == "continuous":
            while True:
                try:
                    decimal_places = int(input("Enter number of decimal places (>=0): ").strip())
                    if decimal_places >= 0:
                        break
                    else:
                        print("Must be >=0")
                except ValueError:
                    print("Enter an integer")
            col_meta["decimal_places"] = decimal_places

        if col_type == "categorical":
            categories = input("Enter categories separated by commas: ").strip().split(",")
            categories = [c.strip() for c in categories if c.strip()]
            if not categories:
                raise ValueError("At least one category required")
            col_meta["categories"] = categories

        metadata.append(col_meta)

    json_path = path.with_suffix(".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    print(f"\nMetadata saved to {json_path}")
