import pandas as pd

from app import create_app
from finance_analytics.analytics import (
    build_dashboard_analysis_results,
    calculate_extended_metrics,
    calculate_metrics,
    calculate_outlier_sensitivity,
    generate_all_insights,
    generate_dashboard_summary,
    generate_insights,
    get_category_semantic_audit,
    get_category_summary,
    get_monthly_summary,
    get_payment_method_summary,
)
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


def test_extended_analysis_metrics_are_computed():
    raw = pd.DataFrame(
        [
            {
                "Date": "2024-01-01",
                "Transaction Description": "Salary",
                "Category": "Salary",
                "Amount": 1000,
                "Type": "Income",
                "Payment Method": "Bank Transfer",
            },
            {
                "Date": "2024-01-02",
                "Transaction Description": "Groceries",
                "Category": "Food",
                "Amount": 200,
                "Type": "Expense",
                "Payment Method": "Credit Card",
            },
            {
                "Date": "2024-01-03",
                "Transaction Description": "Rent",
                "Category": "Rent",
                "Amount": 100,
                "Type": "Expense",
                "Payment Method": "Debit Card",
            },
            {
                "Date": "2024-02-01",
                "Transaction Description": "Freelance",
                "Category": "Other",
                "Amount": 500,
                "Type": "Income",
                "Payment Method": "E-Wallet",
            },
            {
                "Date": "2024-02-02",
                "Transaction Description": "Groceries",
                "Category": "Food",
                "Amount": 700,
                "Type": "Expense",
                "Payment Method": "Credit Card",
            },
            {
                "Date": "2024-02-03",
                "Transaction Description": "Rent",
                "Category": "Rent",
                "Amount": 300,
                "Type": "Expense",
                "Payment Method": "Debit Card",
            },
        ]
    )

    cleaned, _ = clean_transactions(raw)
    extended = calculate_extended_metrics(cleaned)
    sensitivity = calculate_outlier_sensitivity(cleaned)
    payment_methods = get_payment_method_summary(cleaned)
    insights = generate_insights(cleaned, calculate_metrics(cleaned))

    assert extended["positive_savings_months"] == 1
    assert extended["total_months"] == 2
    assert extended["positive_savings_month_share"] == 50
    assert extended["top_three_category_concentration"] == 100
    assert extended["expense_mean_median_gap"] == 75
    assert sensitivity["capped_net_savings"] == sensitivity["uncapped_net_savings"]
    assert payment_methods.iloc[0]["payment_method"] == "Credit Card"
    assert len(insights) >= 4
    assert {"title", "chart_id", "finding", "interpretation", "recommendation", "severity"}.issubset(
        insights[0]
    )


def test_salary_expense_records_are_reclassified_or_kept_by_description():
    raw = pd.DataFrame(
        [
            {
                "Date": "2024-01-01",
                "Transaction Description": "Monthly salary deposit",
                "Category": "Salary",
                "Amount": 250,
                "Type": "Expense",
            },
            {
                "Date": "2024-01-02",
                "Transaction Description": "Employee salary payroll expense",
                "Category": "Salary",
                "Amount": 100,
                "Type": "Expense",
            }
        ]
    )

    cleaned, _ = clean_transactions(raw)
    audit = get_category_semantic_audit(cleaned)

    assert audit["has_salary_expenses"] is False
    assert cleaned.loc[cleaned["amount"].eq(250), "transaction_type"].iloc[0] == "Income"
    assert cleaned.loc[cleaned["amount"].eq(100), "transaction_type"].iloc[0] == "Expense"
    assert cleaned.loc[cleaned["amount"].eq(100), "category"].iloc[0] == "Payroll Expense"


def test_unknown_categories_are_inferred_from_description():
    raw = pd.DataFrame(
        [
            {
                "Date": "2024-01-01",
                "Transaction Description": "Coffee at cafe",
                "Category": "",
                "Amount": 25,
                "Type": "Expense",
            },
            {
                "Date": "2024-01-02",
                "Transaction Description": "Unclear transaction",
                "Category": None,
                "Amount": 50,
                "Type": "Expense",
            },
        ]
    )

    cleaned, report = clean_transactions(raw)

    assert cleaned.loc[cleaned["amount"].eq(25), "category"].iloc[0] == "Food & Drink"
    assert cleaned.loc[cleaned["amount"].eq(50), "category"].iloc[0] == "Unknown"
    assert report["unknown_categories_inferred"] == 1
    assert report["unknown_categories_remaining"] == 1


def test_dashboard_renders_gap_closure_sections():
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Total income" in html
    assert "Total expenses" in html
    assert "Net savings" in html
    assert "dashboard-summary" not in html
    assert "Key Insight" not in html
    assert "Recommendation" in html
    assert "Conclusion" in html
    assert html.index("Conclusion") < html.index("Recommendation")
    assert "Top expense categories" in html
    assert "monthly trend shows" in html
    assert "Review" in html
    assert "Cleaning Report" in html
    assert "Advanced Analysis" in html
    assert "Monthly Summary" in html
    assert "Payment Method Summary" in html
    assert "Outlier Sensitivity" in html
    assert "Dataset semantic audit" not in html
    assert "No salary-as-expense issue was detected" not in html
    assert "Salary records reclassified as income" in html
    assert "Unknown categories inferred" in html


def test_dashboard_summary_groups_dynamic_financial_story():
    raw = pd.DataFrame(
        [
            {
                "Date": "2024-01-01",
                "Transaction Description": "Salary",
                "Category": "Salary",
                "Amount": 1000,
                "Type": "Income",
                "Payment Method": "Bank Transfer",
            },
            {
                "Date": "2024-01-05",
                "Transaction Description": "Trip",
                "Category": "Travel",
                "Amount": 600,
                "Type": "Expense",
                "Payment Method": "Credit Card",
            },
            {
                "Date": "2024-02-06",
                "Transaction Description": "Rent",
                "Category": "Rent",
                "Amount": 1200,
                "Type": "Expense",
                "Payment Method": "Credit Card",
            },
        ]
    )

    cleaned, _ = clean_transactions(raw)
    analysis_results = build_dashboard_analysis_results(cleaned, calculate_metrics(cleaned))
    summary = generate_dashboard_summary(analysis_results)

    assert len(summary["key_insights"]) >= 4
    assert len(summary["recommendations"]) >= 4
    assert "monthly_trends" in summary["charts"]
    assert "top_expense_categories" in summary["charts"]
    assert "conclusion" in summary["charts"]["top_expense_categories"]
    assert "conclusion" in summary["charts"]["expense_share_by_category"]
    assert "conclusion" in summary["charts"]["transaction_amount_distribution"]
    assert "conclusion" in summary["charts"]["payment_method_expenses"]
    assert "Rent" in " ".join(summary["key_insights"])
    assert "Credit Card" in " ".join(summary["recommendations"])
    assert "Rent" in summary["charts"]["top_expense_categories"]["key_insight"]
    assert "Credit Card" in summary["charts"]["payment_method_expenses"]["recommendation"]
    assert "The user should monitor monthly cash flow more consistently" in summary["charts"]["monthly_trends"]["recommendation"]
    assert "The user should prioritize reviewing the Rent category" in summary["charts"]["top_expense_categories"]["recommendation"]
    assert "The user should review the" in summary["charts"]["transaction_amount_distribution"]["recommendation"]
    assert "Rent is the largest expense category" in summary["charts"]["top_expense_categories"]["conclusion"]
    assert "Credit Card is the most used payment method" in summary["charts"]["payment_method_expenses"]["conclusion"]
    assert "descriptive results based on the available dataset" in summary["conclusion"]


def test_graph_specific_insights_cover_required_findings():
    raw = pd.DataFrame(
        [
            {
                "Date": "2024-01-01",
                "Transaction Description": "Salary",
                "Category": "Salary",
                "Amount": 1000,
                "Type": "Income",
                "Payment Method": "Bank Transfer",
            },
            {
                "Date": "2024-01-05",
                "Transaction Description": "Trip",
                "Category": "Travel",
                "Amount": 600,
                "Type": "Expense",
                "Payment Method": "Credit Card",
            },
            {
                "Date": "2024-01-06",
                "Transaction Description": "Dinner",
                "Category": "Food",
                "Amount": 200,
                "Type": "Expense",
                "Payment Method": "Credit Card",
            },
            {
                "Date": "2024-02-07",
                "Transaction Description": "Rent",
                "Category": "Rent",
                "Amount": 1200,
                "Type": "Expense",
                "Payment Method": "Debit Card",
            },
        ]
    )

    cleaned, _ = clean_transactions(raw)
    insights = generate_all_insights(cleaned, calculate_metrics(cleaned))

    overall = insights["overall_summary"]
    category = insights["top_expense_categories"][0]
    monthly = insights["monthly_trends"]
    payment = insights["payment_method_expenses"][0]

    assert any(item["title"] == "Negative Net Savings" for item in overall)
    assert any(item["severity"] == "high" for item in monthly)
    assert category["title"] == "Highest Expense Category"
    assert category["chart_id"] == "top_expense_categories"
    assert "Rent" in category["finding"]
    assert category["severity"] == "medium"
    assert any(item["title"] == "Highest Spending Month" for item in monthly)
    assert payment["title"] == "Dominant Payment Method"
    assert payment["chart_id"] == "payment_method_expenses"


def test_no_expense_records_return_safe_expense_insights():
    raw = pd.DataFrame(
        [
            {
                "Date": "2024-01-01",
                "Transaction Description": "Salary",
                "Category": "Salary",
                "Amount": 1000,
                "Type": "Income",
                "Payment Method": "Bank Transfer",
            }
        ]
    )

    cleaned, _ = clean_transactions(raw)
    insights = generate_all_insights(cleaned, calculate_metrics(cleaned))

    assert insights["top_expense_categories"][0]["title"] == "No Expense Categories"
    assert insights["expense_share_by_category"][0]["title"] == "No Expense Share Available"
    assert insights["payment_method_expenses"][0]["title"] == "No Payment Method Expense Data"


def test_no_income_records_avoid_misleading_savings_rate_interpretation():
    raw = pd.DataFrame(
        [
            {
                "Date": "2024-01-01",
                "Transaction Description": "Rent",
                "Category": "Rent",
                "Amount": 1000,
                "Type": "Expense",
                "Payment Method": "Debit Card",
            }
        ]
    )

    cleaned, _ = clean_transactions(raw)
    insights = generate_all_insights(cleaned, calculate_metrics(cleaned))

    assert insights["overall_summary"][0]["title"] == "Missing Income Context"
    assert any(item["title"] == "Income Records Missing" for item in insights["monthly_trends"])


def test_salary_expense_warning_is_removed_after_cleaning_reclassification():
    raw = pd.DataFrame(
        [
            {
                "Date": "2024-01-01",
                "Transaction Description": "Monthly salary",
                "Category": "Salary",
                "Amount": 250,
                "Type": "Expense",
                "Payment Method": "Cash",
            }
        ]
    )

    cleaned, _ = clean_transactions(raw)
    insights = generate_all_insights(cleaned, calculate_metrics(cleaned))

    assert cleaned.loc[0, "transaction_type"] == "Income"
    assert not any(
        item["title"] == "Possible Salary Classification Issue"
        for item in insights["overall_summary"]
    )


def test_unknown_category_warning_remains_when_inference_fails():
    raw = pd.DataFrame(
        [
            {
                "Date": "2024-01-01",
                "Transaction Description": "Unclear transaction",
                "Category": "",
                "Amount": 250,
                "Type": "Expense",
                "Payment Method": "Cash",
            }
        ]
    )

    cleaned, _ = clean_transactions(raw)
    insights = generate_all_insights(cleaned, calculate_metrics(cleaned))

    assert any(item["title"] == "Unknown Categories Present" for item in insights["overall_summary"])
