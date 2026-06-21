import pandas as pd

from finance_analytics.analytics import calculate_metrics, get_category_summary, get_monthly_summary
from finance_analytics.data import clean_transactions


def test_clean_transactions_standardizes_and_engineers_columns():
    raw = pd.DataFrame(
        [
            {
                "Date": "2024-01-01",
                "Transaction Description": " Salary ",
                "Category": "salary",
                "Amount": "$1,000.00",
                "Type": "income",
                "Payment Method": "banktransfer",
            },
            {
                "Date": "2024-01-02",
                "Transaction Description": "Lunch",
                "Category": "food & drink",
                "Amount": "150",
                "Type": "expense",
                "Payment Method": "e wallet",
            },
            {
                "Date": "bad-date",
                "Transaction Description": "Invalid",
                "Category": "Other",
                "Amount": "20",
                "Type": "Expense",
                "Payment Method": None,
            },
        ]
    )

    cleaned, report = clean_transactions(raw)

    assert len(cleaned) == 2
    assert report["invalid_date_rows_removed"] == 1
    assert report["standardized_text_entries"] > 0
    assert "signed_amount" in cleaned.columns
    assert "payment_method" in cleaned.columns
    assert "period" in cleaned.columns
    assert cleaned["payment_method"].tolist() == ["Bank Transfer", "E-Wallet"]
    assert cleaned.loc[cleaned["transaction_type"].eq("Income"), "signed_amount"].iloc[0] == 1000
    assert cleaned.loc[cleaned["transaction_type"].eq("Expense"), "signed_amount"].iloc[0] == -150


def test_calculate_metrics_computes_finance_totals():
    raw = pd.DataFrame(
        [
            {
                "Date": "2024-01-01",
                "Transaction Description": "Salary",
                "Category": "Salary",
                "Amount": 2000,
                "Type": "Income",
            },
            {
                "Date": "2024-01-02",
                "Transaction Description": "Rent",
                "Category": "Rent",
                "Amount": 800,
                "Type": "Expense",
            },
        ]
    )

    cleaned, _ = clean_transactions(raw)
    metrics = calculate_metrics(cleaned)

    assert metrics["total_income"] == 2000
    assert metrics["total_expense"] == 800
    assert metrics["net_savings"] == 1200
    assert metrics["savings_rate"] == 60


def test_grouped_summaries_are_ready_for_charts():
    raw = pd.DataFrame(
        [
            {
                "Date": "2024-01-01",
                "Transaction Description": "Salary",
                "Category": "Salary",
                "Amount": 3000,
                "Type": "Income",
            },
            {
                "Date": "2024-01-03",
                "Transaction Description": "Groceries",
                "Category": "Food",
                "Amount": 500,
                "Type": "Expense",
            },
        ]
    )

    cleaned, _ = clean_transactions(raw)
    monthly = get_monthly_summary(cleaned)
    categories = get_category_summary(cleaned)

    assert monthly.loc[0, "period"] == "2024-01"
    assert monthly.loc[0, "net_savings"] == 2500
    assert categories.loc[0, "category"] == "Food"
