import csv
from pathlib import Path

def save_dataset(data: list[list[any]], original_path: str) -> None:
    original = Path(original_path).with_suffix(".csv")
    if not original.exists():
        raise FileNotFoundError(f"{original} does not exist")

    new_name = original.stem + "_privatized" + original.suffix
    data_path = original.with_name(new_name)

    with open(data_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
