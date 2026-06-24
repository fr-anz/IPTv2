from __future__ import annotations

import pandas as pd
import plotly.express as px

Insight = dict[str, str]


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


def calculate_extended_metrics(data: pd.DataFrame) -> dict[str, float | int]:
    monthly = get_monthly_summary(data)
    categories = get_category_summary(data)
    expenses = data.loc[data["transaction_type"].eq("Expense")]

    positive_months = int(monthly["net_savings"].gt(0).sum())
    total_months = int(len(monthly))
    top_three_concentration = (
        float(categories.head(3)["share_of_expenses"].sum()) if not categories.empty else 0
    )
    outlier_count = int(data["is_outlier"].sum()) if "is_outlier" in data else 0
    outlier_rate = (outlier_count / len(data) * 100) if len(data) else 0
    expense_mean = expenses["amount_cleaned"].mean() if not expenses.empty else 0
    expense_median = expenses["amount_cleaned"].median() if not expenses.empty else 0
    monthly_variance = monthly["net_savings"].var()
    monthly_standard_deviation = monthly["net_savings"].std()

    return {
        "monthly_net_variance": round(
            float(0 if pd.isna(monthly_variance) else monthly_variance),
            2,
        ),
        "monthly_net_standard_deviation": round(
            float(0 if pd.isna(monthly_standard_deviation) else monthly_standard_deviation),
            2,
        ),
        "positive_savings_months": positive_months,
        "total_months": total_months,
        "positive_savings_month_share": round(
            (positive_months / total_months * 100) if total_months else 0,
            2,
        ),
        "top_three_category_concentration": round(top_three_concentration, 2),
        "outlier_transaction_rate": round(float(outlier_rate), 2),
        "expense_mean_median_gap": round(float(expense_mean - expense_median), 2),
    }


def calculate_outlier_sensitivity(data: pd.DataFrame) -> dict[str, float | int]:
    income = data["transaction_type"].eq("Income")
    expense = data["transaction_type"].eq("Expense")

    uncapped_income = data.loc[income, "amount"].sum()
    capped_income = data.loc[income, "amount_cleaned"].sum()
    uncapped_expense = data.loc[expense, "amount"].sum()
    capped_expense = data.loc[expense, "amount_cleaned"].sum()
    uncapped_net = uncapped_income - uncapped_expense
    capped_net = capped_income - capped_expense
    outlier_count = int(data["is_outlier"].sum()) if "is_outlier" in data else 0

    return {
        "uncapped_income": round(float(uncapped_income), 2),
        "capped_income": round(float(capped_income), 2),
        "income_change": round(float(capped_income - uncapped_income), 2),
        "uncapped_expense": round(float(uncapped_expense), 2),
        "capped_expense": round(float(capped_expense), 2),
        "expense_change": round(float(capped_expense - uncapped_expense), 2),
        "uncapped_net_savings": round(float(uncapped_net), 2),
        "capped_net_savings": round(float(capped_net), 2),
        "net_savings_change": round(float(capped_net - uncapped_net), 2),
        "outliers_capped": outlier_count,
        "outlier_transaction_rate": round((outlier_count / len(data) * 100) if len(data) else 0, 2),
    }


def get_category_semantic_audit(data: pd.DataFrame) -> dict[str, float | int | bool]:
    salary_expenses = data.loc[
        data["category"].eq("Salary") & data["transaction_type"].eq("Expense")
    ]
    salary_income = data.loc[data["category"].eq("Salary") & data["transaction_type"].eq("Income")]

    return {
        "has_salary_expenses": bool(len(salary_expenses)),
        "salary_expense_count": int(len(salary_expenses)),
        "salary_expense_total": round(float(salary_expenses["amount_cleaned"].sum()), 2),
        "salary_income_count": int(len(salary_income)),
        "salary_income_total": round(float(salary_income["amount_cleaned"].sum()), 2),
    }


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
        labels={"category": "Category", "total_amount": "Total Expense"},
    )
    line_chart = px.line(
        monthly,
        x="period",
        y=["Income", "Expense", "net_savings"],
        labels={"period": "Month", "value": "Amount", "variable": "Measure"},
        markers=True,
    )
    pie_chart = px.pie(
        categories.head(8),
        values="total_amount",
        names="category",
    )
    histogram = px.histogram(
        data,
        x="amount_cleaned",
        color="transaction_type",
        labels={"amount_cleaned": "Transaction Amount", "transaction_type": "Type"},
        nbins=30,
    )
    payment_chart = px.bar(
        payment_methods,
        x="payment_method",
        y="total_amount",
        labels={"payment_method": "Payment Method", "total_amount": "Total Expense"},
    )

    return {
        "bar_chart": _to_html(bar_chart, include_plotlyjs=True),
        "line_chart": _to_html(line_chart),
        "pie_chart": _to_html(pie_chart),
        "histogram": _to_html(histogram),
        "payment_chart": _to_html(payment_chart),
    }


def generate_insights(data: pd.DataFrame, metrics: dict[str, float | int | str]) -> list[Insight]:
    return generate_overall_insights(data, metrics)


def generate_all_insights(
    data: pd.DataFrame,
    metrics: dict[str, float | int | str],
) -> dict[str, list[Insight]]:
    return {
        "overall_summary": generate_overall_insights(data, metrics),
        "top_expense_categories": generate_category_insight(data),
        "monthly_trends": generate_monthly_trend_insight(data, metrics),
        "expense_share_by_category": generate_expense_share_insight(data),
        "transaction_amount_distribution": generate_amount_distribution_insight(data),
        "payment_method_expenses": generate_payment_method_insight(data),
    }


def generate_overall_insights(
    data: pd.DataFrame,
    metrics: dict[str, float | int | str],
) -> list[Insight]:
    monthly = get_monthly_summary(data)
    categories = get_category_summary(data)
    payment_methods = get_payment_method_summary(data)
    income_count = int(data["transaction_type"].eq("Income").sum())
    expense_count = int(data["transaction_type"].eq("Expense").sum())
    warnings = detect_data_quality_warnings(data)

    insights: list[Insight] = []

    if income_count == 0:
        insights.append(
            _make_insight(
                "Missing Income Context",
                "overall_summary",
                "The cleaned dataset contains no income records.",
                (
                    "This limits savings-rate interpretation because income is needed to "
                    "compare cash inflows against expenses."
                ),
                "Add or verify income transactions before making conclusions about savings performance.",
                "medium",
            )
        )
    elif metrics["net_savings"] < 0 or metrics["savings_rate"] < 0:
        insights.append(
            _make_insight(
                "Negative Net Savings",
                "overall_summary",
                (
                    f"Net savings is {metrics['net_savings']:,.2f}, with a savings rate of "
                    f"{metrics['savings_rate']:,.2f}%."
                ),
                (
                    "This suggests that total expenses are higher than total income for the "
                    "analyzed period."
                ),
                (
                    "Review the highest spending categories and months first, then set a "
                    "monthly savings target before discretionary spending."
                ),
                "high",
            )
        )
    else:
        insights.append(
            _make_insight(
                "Positive Net Savings",
                "overall_summary",
                (
                    f"Net savings is {metrics['net_savings']:,.2f}, with a savings rate of "
                    f"{metrics['savings_rate']:,.2f}%."
                ),
                "This suggests that income is currently greater than expenses in the dataset.",
                "Continue tracking monthly cash flow and protect the categories contributing most to savings.",
                "low",
            )
        )

    if not categories.empty:
        top_category = categories.iloc[0]
        insights.append(
            _make_insight(
                "Largest Expense Area",
                "overall_summary",
                (
                    f"{top_category['category']} is the highest expense category at "
                    f"{top_category['share_of_expenses']:,.2f}% of total expenses."
                ),
                "This highlights the category with the largest effect on total spending.",
                "Review transactions in this category and set a budget threshold if the share remains high.",
                _severity_for_share(float(top_category["share_of_expenses"]), 10),
            )
        )

    if not monthly.empty and monthly["Expense"].sum() > 0:
        highest_expense_month = monthly.sort_values("Expense", ascending=False).iloc[0]
        insights.append(
            _make_insight(
                "Peak Spending Month",
                "overall_summary",
                (
                    f"{_format_period(highest_expense_month['period'])} recorded the highest "
                    f"expenses at {highest_expense_month['Expense']:,.2f}."
                ),
                "This may indicate unusual, seasonal, or one-time spending activity.",
                "Filter that month and review the largest transactions before setting future budgets.",
                "medium",
            )
        )

    if not payment_methods.empty:
        top_payment_method = payment_methods.iloc[0]
        insights.append(
            _make_insight(
                "Dominant Payment Method",
                "overall_summary",
                (
                    f"{top_payment_method['payment_method']} represents "
                    f"{top_payment_method['share_of_expenses']:,.2f}% of total expenses."
                ),
                "This suggests that one payment method plays a major role in spending behavior.",
                "Review this payment method by category and consider a monthly spending limit.",
                _severity_for_share(float(top_payment_method["share_of_expenses"]), 20),
            )
        )

    insights.append(
        _make_insight(
            "Transaction Mix",
            "overall_summary",
            f"The dataset contains {expense_count} expense records and {income_count} income records.",
            (
                "This highlights whether spending or income behavior has more transaction-level "
                "detail in the dataset."
            ),
            "Keep both income and expense records updated so the dashboard can compare cash flow reliably.",
            "low" if expense_count > income_count else "low",
        )
    )

    insights.extend(warnings[:2])
    return insights


def generate_category_insight(data: pd.DataFrame) -> list[Insight]:
    categories = get_category_summary(data)
    if categories.empty:
        return [
            _make_insight(
                "No Expense Categories",
                "top_expense_categories",
                "No expense records are available for category ranking.",
                "This means the chart cannot identify a highest spending category.",
                "Verify that expense transactions are present and correctly classified before reviewing category budgets.",
                "low",
            )
        ]

    top_category = categories.iloc[0]
    share = float(top_category["share_of_expenses"])
    recommendation = f"Review {top_category['category']} transactions"
    if share > 10:
        recommendation += " and set a monthly or quarterly budget limit for this category."
    else:
        recommendation += " and continue monitoring whether its share increases."

    return [
        _make_insight(
            "Highest Expense Category",
            "top_expense_categories",
            f"{top_category['category']} accounts for {share:,.2f}% of total expenses.",
            (
                f"This suggests that {top_category['category']} is the largest contributor "
                "to overall spending."
            ),
            recommendation,
            _severity_for_share(share, 10),
        )
    ]


def generate_monthly_trend_insight(
    data: pd.DataFrame,
    metrics: dict[str, float | int | str],
) -> list[Insight]:
    monthly = get_monthly_summary(data)
    if monthly.empty:
        return [
            _make_insight(
                "No Monthly Trend Available",
                "monthly_trends",
                "No dated transaction records are available for monthly analysis.",
                "This prevents comparison of income, expenses, and net savings over time.",
                "Verify transaction dates before using monthly trend results.",
                "low",
            )
        ]

    insights: list[Insight] = []
    if monthly["Expense"].sum() > 0:
        highest_expense_month = monthly.sort_values("Expense", ascending=False).iloc[0]
        negative_months = monthly.loc[monthly["net_savings"] < 0, "period"]
        negative_count = int(len(negative_months))
        insights.append(
            _make_insight(
                "Highest Spending Month",
                "monthly_trends",
                (
                    f"{_format_period(highest_expense_month['period'])} recorded the highest "
                    f"total expenses at {highest_expense_month['Expense']:,.2f}."
                ),
                (
                    "This may indicate unusual, seasonal, or one-time spending activity. "
                    f"{negative_count} month(s) show negative net savings."
                ),
                (
                    f"Filter transactions from {_format_period(highest_expense_month['period'])} "
                    "and review the largest expenses in that period."
                ),
                "medium",
            )
        )

    if metrics["total_income"] == 0:
        insights.append(
            _make_insight(
                "Income Records Missing",
                "monthly_trends",
                "No income records are available for trend comparison.",
                "This prevents reliable interpretation of savings rate and net cash flow.",
                "Add income transactions or mark income records correctly before interpreting savings performance.",
                "medium",
            )
        )
    elif metrics["net_savings"] < 0 or metrics["savings_rate"] < 0:
        insights.append(
            _make_insight(
                "Cash-Flow Risk",
                "monthly_trends",
                (
                    f"Overall net savings is {metrics['net_savings']:,.2f}, and the savings "
                    f"rate is {metrics['savings_rate']:,.2f}%."
                ),
                "This may indicate cash-flow risk because expenses exceed income across the dataset.",
                "Prioritize months with negative net savings and reduce flexible expenses first.",
                "high",
            )
        )

    return insights


def generate_expense_share_insight(data: pd.DataFrame) -> list[Insight]:
    categories = get_category_summary(data)
    if categories.empty:
        return [
            _make_insight(
                "No Expense Share Available",
                "expense_share_by_category",
                "No expense records are available for category share analysis.",
                "This means the chart cannot show how expenses are distributed.",
                "Verify expense classifications before comparing spending shares.",
                "low",
            )
        ]

    top_three_share = float(categories.head(3)["share_of_expenses"].sum())
    category_count = int(len(categories))
    if top_three_share >= 40:
        interpretation = (
            "This suggests that spending is concentrated in a small group of categories."
        )
    else:
        interpretation = "This suggests that spending is spread across several categories."
    recommendation = "Focus first on the categories with the largest shares."
    if category_count > 8:
        recommendation += " Group smaller categories into Other to improve readability."

    return [
        _make_insight(
            "Expense Share Pattern",
            "expense_share_by_category",
            (
                f"The top three expense categories represent {top_three_share:,.2f}% "
                f"of expenses across {category_count} category/categories."
            ),
            interpretation,
            recommendation,
            "medium" if top_three_share >= 40 else "low",
        )
    ]


def generate_amount_distribution_insight(data: pd.DataFrame) -> list[Insight]:
    if data.empty:
        return [
            _make_insight(
                "No Amount Distribution Available",
                "transaction_amount_distribution",
                "No cleaned transaction records are available for amount distribution analysis.",
                "This prevents review of common transaction sizes and unusual values.",
                "Verify that valid transaction amounts exist before interpreting the distribution.",
                "low",
            )
        ]

    amount_band = data["amount_band"].mode().iloc[0] if "amount_band" in data else "Unknown"
    outlier_count = int(data["is_outlier"].sum()) if "is_outlier" in data else 0
    if outlier_count:
        interpretation = (
            "Outliers may represent valid large transactions or possible data entry issues."
        )
        recommendation = "Review flagged outlier transactions before final interpretation."
        severity = "medium"
    else:
        interpretation = "This suggests that transaction amounts do not contain flagged high outliers."
        recommendation = "Continue monitoring transaction size bands for changes in spending behavior."
        severity = "low"

    return [
        _make_insight(
            "Transaction Amount Pattern",
            "transaction_amount_distribution",
            (
                f"Most transactions fall within the {amount_band} amount band, and "
                f"{outlier_count} transaction(s) were flagged as outliers."
            ),
            interpretation,
            recommendation,
            severity,
        )
    ]


def generate_payment_method_insight(data: pd.DataFrame) -> list[Insight]:
    payment_methods = get_payment_method_summary(data)
    if payment_methods.empty:
        return [
            _make_insight(
                "No Payment Method Expense Data",
                "payment_method_expenses",
                "No expense records are available for payment method analysis.",
                "This means the chart cannot identify a dominant spending method.",
                "Verify expense transactions and payment method values before interpreting this chart.",
                "low",
            )
        ]

    top_payment_method = payment_methods.iloc[0]
    share = float(top_payment_method["share_of_expenses"])
    return [
        _make_insight(
            "Dominant Payment Method",
            "payment_method_expenses",
            f"{top_payment_method['payment_method']} represents {share:,.2f}% of total expenses.",
            (
                "This suggests that this payment method plays a major role in spending behavior."
            ),
            (
                f"Review {top_payment_method['payment_method']} transactions by category and "
                "consider setting a spending limit for this payment method."
            ),
            _severity_for_share(share, 20),
        )
    ]


def detect_data_quality_warnings(data: pd.DataFrame) -> list[Insight]:
    warnings: list[Insight] = []
    salary_expenses = data.loc[
        data["category"].eq("Salary") & data["transaction_type"].eq("Expense")
    ]
    unknown_categories = int(data["category"].eq("Unknown").sum()) if "category" in data else 0
    unknown_payment_methods = (
        int(data["payment_method"].eq("Unknown").sum()) if "payment_method" in data else 0
    )

    if len(salary_expenses):
        warnings.append(
            _make_insight(
                "Possible Salary Classification Issue",
                "overall_summary",
                (
                    f"Salary appears under expense categories in {len(salary_expenses)} "
                    f"record(s), totaling {salary_expenses['amount_cleaned'].sum():,.2f}."
                ),
                (
                    "This should be reviewed because salary is normally classified as income "
                    "in a personal finance dataset."
                ),
                "Verify whether these records are true expenses or should be reclassified as income.",
                "low",
            )
        )

    if unknown_categories:
        warnings.append(
            _make_insight(
                "Unknown Categories Present",
                "overall_summary",
                f"{unknown_categories} transaction(s) use Unknown as the category.",
                "This may reduce the accuracy of category-level spending interpretation.",
                "Review Unknown category records and assign more specific categories where possible.",
                "low",
            )
        )

    if unknown_payment_methods:
        warnings.append(
            _make_insight(
                "Unknown Payment Methods Present",
                "overall_summary",
                f"{unknown_payment_methods} transaction(s) use Unknown as the payment method.",
                "This may reduce the accuracy of payment-method analysis.",
                "Review Unknown payment method records before making payment behavior conclusions.",
                "low",
            )
        )

    return warnings


def get_insights_for_chart(insights_by_chart: dict[str, list[Insight]], chart_id: str) -> list[Insight]:
    return insights_by_chart.get(chart_id, [])


def _make_insight(
    title: str,
    chart_id: str,
    finding: str,
    interpretation: str,
    recommendation: str,
    severity: str,
) -> Insight:
    return {
        "title": title,
        "chart_id": chart_id,
        "finding": finding,
        "interpretation": interpretation,
        "recommendation": recommendation,
        "severity": severity,
    }


def _severity_for_share(share: float, threshold: float) -> str:
    return "medium" if share > threshold else "low"


def _format_period(period: str) -> str:
    parsed = pd.Period(period, freq="M")
    return parsed.strftime("%B %Y")


def _to_html(figure, include_plotlyjs: bool = False) -> str:
    figure.update_layout(
        template="plotly_white",
        margin=dict(l=42, r=24, t=24, b=42),
        font=dict(family='Aptos, "Segoe UI", sans-serif', color="#334155"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return figure.to_html(
        full_html=False,
        include_plotlyjs=include_plotlyjs,
        default_height="360px",
        config={"responsive": True},
    )
