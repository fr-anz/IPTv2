from __future__ import annotations

import pandas as pd
import plotly.express as px


def calculate_metrics(data: pd.DataFrame) -> dict[str, float | int | str]:
    income = data.loc[data["transaction_type"].eq("Income"), "amount_cleaned"].sum()
    expense = data.loc[data["transaction_type"].eq("Expense"), "amount_cleaned"].sum()
    net_savings = income - expense
    savings_rate = (net_savings / income * 100) if income else 0

    return {
        "total_transactions": int(len(data)),
        "total_income": round(float(income), 2),
        "total_expense": round(float(expense), 2),
        "net_savings": round(float(net_savings), 2),
        "savings_rate": round(float(savings_rate), 2),
        "average_transaction": round(float(data["amount_cleaned"].mean()), 2),
        "median_transaction": round(float(data["amount_cleaned"].median()), 2),
        "largest_transaction": round(float(data["amount_cleaned"].max()), 2),
        "date_range": f"{data['date'].min().date()} to {data['date'].max().date()}",
    }


def get_monthly_summary(data: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        data.pivot_table(
            index="period",
            columns="transaction_type",
            values="amount_cleaned",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )

    for column in ["Income", "Expense"]:
        if column not in monthly:
            monthly[column] = 0

    monthly["net_savings"] = monthly["Income"] - monthly["Expense"]
    return monthly.sort_values("period")


def get_category_summary(data: pd.DataFrame) -> pd.DataFrame:
    expenses = data.loc[data["transaction_type"].eq("Expense")]
    summary = (
        expenses.groupby("category", as_index=False)
        .agg(total_amount=("amount_cleaned", "sum"), transaction_count=("amount_cleaned", "size"))
        .sort_values("total_amount", ascending=False)
    )
    total_expenses = summary["total_amount"].sum()
    summary["share_of_expenses"] = (summary["total_amount"] / total_expenses * 100).round(2)
    summary["total_amount"] = summary["total_amount"].round(2)
    return summary


def get_payment_method_summary(data: pd.DataFrame) -> pd.DataFrame:
    expenses = data.loc[data["transaction_type"].eq("Expense")]
    summary = (
        expenses.groupby("payment_method", as_index=False)
        .agg(total_amount=("amount_cleaned", "sum"), transaction_count=("amount_cleaned", "size"))
        .sort_values("total_amount", ascending=False)
    )
    total_expenses = summary["total_amount"].sum()
    summary["share_of_expenses"] = (summary["total_amount"] / total_expenses * 100).round(2)
    summary["total_amount"] = summary["total_amount"].round(2)
    return summary


def get_statistics_table(data: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"metric": "Mean", "value": data["amount_cleaned"].mean()},
            {"metric": "Median", "value": data["amount_cleaned"].median()},
            {"metric": "Mode", "value": data["amount_cleaned"].mode().iloc[0]},
            {"metric": "Standard Deviation", "value": data["amount_cleaned"].std()},
            {"metric": "Minimum", "value": data["amount_cleaned"].min()},
            {"metric": "Maximum", "value": data["amount_cleaned"].max()},
        ]
    ).assign(value=lambda frame: frame["value"].round(2))


def build_dashboard_charts(data: pd.DataFrame) -> dict[str, str]:
    monthly = get_monthly_summary(data)
    categories = get_category_summary(data)
    payment_methods = get_payment_method_summary(data)

    bar_chart = px.bar(
        categories.head(10),
        x="category",
        y="total_amount",
        title="Top Expense Categories",
        labels={"category": "Category", "total_amount": "Total Expense"},
    )
    line_chart = px.line(
        monthly,
        x="period",
        y=["Income", "Expense", "net_savings"],
        title="Monthly Income, Expenses, and Net Savings",
        labels={"period": "Month", "value": "Amount", "variable": "Measure"},
        markers=True,
    )
    pie_chart = px.pie(
        categories.head(8),
        values="total_amount",
        names="category",
        title="Expense Share by Category",
    )
    histogram = px.histogram(
        data,
        x="amount_cleaned",
        color="transaction_type",
        title="Transaction Amount Distribution",
        labels={"amount_cleaned": "Transaction Amount", "transaction_type": "Type"},
        nbins=30,
    )
    payment_chart = px.bar(
        payment_methods,
        x="payment_method",
        y="total_amount",
        title="Expense Totals by Payment Method",
        labels={"payment_method": "Payment Method", "total_amount": "Total Expense"},
    )

    return {
        "bar_chart": _to_html(bar_chart, include_plotlyjs=True),
        "line_chart": _to_html(line_chart),
        "pie_chart": _to_html(pie_chart),
        "histogram": _to_html(histogram),
        "payment_chart": _to_html(payment_chart),
    }


def generate_insights(data: pd.DataFrame, metrics: dict[str, float | int | str]) -> list[str]:
    monthly = get_monthly_summary(data)
    categories = get_category_summary(data)

    highest_expense_month = monthly.sort_values("Expense", ascending=False).iloc[0]
    top_category = categories.iloc[0]
    payment_methods = get_payment_method_summary(data)
    top_payment_method = payment_methods.iloc[0]
    income_count = int(data["transaction_type"].eq("Income").sum())
    expense_count = int(data["transaction_type"].eq("Expense").sum())

    return [
        (
            f"Expenses are concentrated in {top_category['category']}, which accounts for "
            f"{top_category['share_of_expenses']}% of total expenses."
        ),
        (
            f"The highest spending month is {highest_expense_month['period']} with "
            f"{highest_expense_month['Expense']:.2f} in expenses."
        ),
        (
            f"The dataset contains {expense_count} expense records and {income_count} income records, "
            "so spending behavior has more transaction-level detail than income behavior."
        ),
        (
            f"The current net savings is {metrics['net_savings']:.2f}, with a savings rate of "
            f"{metrics['savings_rate']:.2f}%."
        ),
        (
            f"{top_payment_method['payment_method']} is the highest expense payment method, "
            f"representing {top_payment_method['share_of_expenses']}% of spending."
        ),
    ]


def _to_html(figure, include_plotlyjs: bool = False) -> str:
    figure.update_layout(template="plotly_white", margin=dict(l=40, r=24, t=64, b=40))
    return figure.to_html(
        full_html=False,
        include_plotlyjs=include_plotlyjs,
        config={"responsive": True},
    )
