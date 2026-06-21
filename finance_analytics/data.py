from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "Date",
    "Transaction Description",
    "Category",
    "Amount",
    "Type",
}

COLUMN_RENAMES = {
    "Date": "date",
    "Transaction Description": "description",
    "Category": "category",
    "Amount": "amount",
    "Type": "transaction_type",
    "Payment Method": "payment_method",
}

VALID_TYPES = {"Income", "Expense"}
PAYMENT_METHOD_ALIASES = {
    "": "Unknown",
    "nan": "Unknown",
    "none": "Unknown",
    "cash": "Cash",
    "debit": "Debit Card",
    "debit card": "Debit Card",
    "debitcard": "Debit Card",
    "credit": "Credit Card",
    "credit card": "Credit Card",
    "creditcard": "Credit Card",
    "bank": "Bank Transfer",
    "bank transfer": "Bank Transfer",
    "banktransfer": "Bank Transfer",
    "transfer": "Bank Transfer",
    "e-wallet": "E-Wallet",
    "ewallet": "E-Wallet",
    "e wallet": "E-Wallet",
    "digital wallet": "E-Wallet",
    "unknown": "Unknown",
}


@dataclass(frozen=True)
class CleaningReport:
    original_rows: int
    cleaned_rows: int
    removed_rows: int
    missing_values_filled: int
    duplicates_removed: int
    invalid_amount_rows_removed: int
    invalid_date_rows_removed: int
    invalid_type_rows_removed: int
    standardized_text_entries: int
    outliers_capped: int
    engineered_columns: list[str]

    def as_dict(self) -> dict[str, int | list[str]]:
        return {
            "original_rows": self.original_rows,
            "cleaned_rows": self.cleaned_rows,
            "removed_rows": self.removed_rows,
            "missing_values_filled": self.missing_values_filled,
            "duplicates_removed": self.duplicates_removed,
            "invalid_amount_rows_removed": self.invalid_amount_rows_removed,
            "invalid_date_rows_removed": self.invalid_date_rows_removed,
            "invalid_type_rows_removed": self.invalid_type_rows_removed,
            "standardized_text_entries": self.standardized_text_entries,
            "outliers_capped": self.outliers_capped,
            "engineered_columns": self.engineered_columns,
        }


def load_transactions(source: str | Path | BinaryIO) -> pd.DataFrame:
    """Load a finance transaction CSV and verify the expected source columns."""
    data = pd.read_csv(source)
    missing_columns = REQUIRED_COLUMNS.difference(data.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"The uploaded dataset is missing required columns: {missing}")

    return data


def clean_transactions(raw_data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int | list[str]]]:
    """Clean the transaction dataset and add analytics-ready derived attributes."""
    original_rows = len(raw_data)
    data = raw_data.copy()
    data = data.rename(columns=COLUMN_RENAMES)
    if "payment_method" not in data:
        data["payment_method"] = "Unknown"

    text_columns = ["description", "category", "transaction_type", "payment_method"]
    missing_values_before = _count_missing_like(data, text_columns + ["date", "amount"])
    text_values_before = data[text_columns].copy()

    for column in text_columns:
        data[column] = data[column].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")

    data["category"] = data["category"].replace("", "Unknown").str.title()
    data["transaction_type"] = data["transaction_type"].str.strip().str.title()
    data["payment_method"] = data["payment_method"].map(_normalize_payment_method)
    standardized_text_entries = _count_standardized_entries(text_values_before, data[text_columns])

    duplicates_before = len(data)
    data = data.drop_duplicates()
    duplicates_removed = duplicates_before - len(data)

    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    invalid_date_rows = int(data["date"].isna().sum())
    data = data.dropna(subset=["date"])

    data["amount"] = pd.to_numeric(_normalize_amount_values(data["amount"]), errors="coerce")
    invalid_amount_mask = data["amount"].isna() | (data["amount"] <= 0)
    invalid_amount_rows = int(invalid_amount_mask.sum())
    data = data.loc[~invalid_amount_mask].copy()

    invalid_type_mask = ~data["transaction_type"].isin(VALID_TYPES)
    invalid_type_rows = int(invalid_type_mask.sum())
    data = data.loc[~invalid_type_mask].copy()

    outlier_cap = _calculate_iqr_upper_cap(data["amount"])
    data["is_outlier"] = data["amount"] > outlier_cap
    outliers_capped = int(data["is_outlier"].sum())
    data["amount_cleaned"] = data["amount"].clip(upper=outlier_cap).round(2)

    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month
    data["month_name"] = data["date"].dt.month_name()
    data["period"] = data["date"].dt.to_period("M").astype(str)
    data["quarter"] = "Q" + data["date"].dt.quarter.astype(str)
    data["signed_amount"] = np.where(
        data["transaction_type"].eq("Income"),
        data["amount_cleaned"],
        -data["amount_cleaned"],
    )
    data["amount_band"] = pd.cut(
        data["amount_cleaned"],
        bins=[0, 500, 1000, 2000, np.inf],
        labels=["Low", "Medium", "High", "Very High"],
        include_lowest=True,
    ).astype(str)

    data = data.sort_values("date").reset_index(drop=True)

    engineered_columns = [
        "amount_cleaned",
        "is_outlier",
        "year",
        "month",
        "month_name",
        "period",
        "quarter",
        "signed_amount",
        "amount_band",
    ]
    report = CleaningReport(
        original_rows=original_rows,
        cleaned_rows=len(data),
        removed_rows=original_rows - len(data),
        missing_values_filled=missing_values_before,
        duplicates_removed=duplicates_removed,
        invalid_amount_rows_removed=invalid_amount_rows,
        invalid_date_rows_removed=invalid_date_rows,
        invalid_type_rows_removed=invalid_type_rows,
        standardized_text_entries=standardized_text_entries,
        outliers_capped=outliers_capped,
        engineered_columns=engineered_columns,
    )

    return data, report.as_dict()


def _calculate_iqr_upper_cap(series: pd.Series) -> float:
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    if pd.isna(iqr) or iqr == 0:
        return float(series.max())

    return float(q3 + (1.5 * iqr))


def _count_missing_like(data: pd.DataFrame, columns: list[str]) -> int:
    values = data[columns]
    blank_strings = values.map(lambda value: isinstance(value, str) and value.strip() == "").sum().sum()
    return int(values.isna().sum().sum() + blank_strings)


def _count_standardized_entries(before: pd.DataFrame, after: pd.DataFrame) -> int:
    comparable_before = before.map(_clean_compare_value)
    comparable_after = after.map(_clean_compare_value)
    return int((comparable_before != comparable_after).sum().sum())


def _normalize_amount_values(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )


def _clean_compare_value(value) -> str:
    if pd.isna(value):
        return "Unknown"
    cleaned = str(value).strip()
    return cleaned if cleaned else "Unknown"


def _normalize_payment_method(value: str) -> str:
    normalized = str(value).strip().lower().replace("_", " ").replace("-", " ")
    normalized = " ".join(normalized.split())
    alias_key = normalized.replace(" ", "") if normalized not in PAYMENT_METHOD_ALIASES else normalized
    return PAYMENT_METHOD_ALIASES.get(alias_key, PAYMENT_METHOD_ALIASES.get(normalized, "Unknown"))
