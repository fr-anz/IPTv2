from __future__ import annotations

import argparse
from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from finance_analytics.data import clean_transactions, load_transactions


DEFAULT_INPUT = BASE_DIR / "data" / "raw" / "raw_personal_finance_dataset.csv"
DEFAULT_OUTPUT = BASE_DIR / "data" / "processed" / "cleaned_personal_finance_dataset.csv"


def main() -> None:
    args = parse_args()
    source = args.input or DEFAULT_INPUT
    destination = args.output

    raw_data = load_transactions(source)
    cleaned_data, report = clean_transactions(raw_data)

    destination.parent.mkdir(parents=True, exist_ok=True)
    cleaned_data.to_csv(destination, index=False)

    print(f"Loaded raw dataset: {source}")
    print(f"Saved cleaned dataset: {destination}")
    print(f"Original rows: {report['original_rows']}")
    print(f"Cleaned rows: {report['cleaned_rows']}")
    print(f"Rows removed: {report['removed_rows']}")
    print(f"Missing values filled: {report['missing_values_filled']}")
    print(f"Duplicates removed: {report['duplicates_removed']}")
    print(f"Invalid amounts removed: {report['invalid_amount_rows_removed']}")
    print(f"Invalid dates removed: {report['invalid_date_rows_removed']}")
    print(f"Invalid types removed: {report['invalid_type_rows_removed']}")
    print(f"Text entries standardized: {report['standardized_text_entries']}")
    print(f"Outliers capped: {report['outliers_capped']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean the raw personal finance dataset and export a processed CSV."
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Raw CSV to clean. Defaults to data/raw/raw_personal_finance_dataset.csv.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination for the cleaned CSV.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
