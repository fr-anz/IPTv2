from __future__ import annotations

import pandas as pd
import plotly.express as px

Insight = dict[str, str]
AnalysisResults = dict[str, object]
DashboardSummary = dict[str, object]

CHART_PALETTE = [
    "#2563eb",
    "#f97316",
    "#16a34a",
    "#7c3aed",
    "#e11d48",
    "#0891b2",
    "#d97706",
    "#64748b",
]
MEASURE_COLORS = {
    "Income": "#16a34a",
    "Expense": "#dc2626",
    "net_savings": "#2563eb",
}


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
        color="category",
        labels={"category": "Category", "total_amount": "Total Expense"},
        color_discrete_sequence=CHART_PALETTE,
    )
    bar_chart.update_layout(showlegend=False)
    line_chart = px.line(
        monthly,
        x="period",
        y=["Income", "Expense", "net_savings"],
        labels={"period": "Month", "value": "Amount", "variable": "Measure"},
        markers=True,
        color_discrete_map=MEASURE_COLORS,
    )
    pie_chart = px.pie(
        categories.head(8),
        values="total_amount",
        names="category",
        hole=0.56,
        color_discrete_sequence=CHART_PALETTE,
    )
    histogram = px.histogram(
        data,
        x="amount_cleaned",
        color="transaction_type",
        labels={"amount_cleaned": "Transaction Amount", "transaction_type": "Type"},
        nbins=30,
        color_discrete_map=MEASURE_COLORS,
    )
    payment_chart = px.bar(
        payment_methods,
        x="payment_method",
        y="total_amount",
        color="payment_method",
        labels={"payment_method": "Payment Method", "total_amount": "Total Expense"},
        color_discrete_sequence=CHART_PALETTE,
    )
    payment_chart.update_layout(showlegend=False)

    return {
        "bar_chart": _to_html(bar_chart, include_plotlyjs=True),
        "line_chart": _to_html(line_chart),
        "pie_chart": _to_html(pie_chart),
        "histogram": _to_html(histogram),
        "payment_chart": _to_html(payment_chart),
    }


def build_dashboard_analysis_results(
    data: pd.DataFrame,
    metrics: dict[str, float | int | str],
) -> AnalysisResults:
    monthly = get_monthly_summary(data)
    categories = get_category_summary(data)
    payment_methods = get_payment_method_summary(data)
    extended_metrics = calculate_extended_metrics(data)
    outlier_sensitivity = calculate_outlier_sensitivity(data)

    highest_expense_month = None
    if not monthly.empty and monthly["Expense"].sum() > 0:
        row = monthly.sort_values("Expense", ascending=False).iloc[0]
        highest_expense_month = {
            "period": _format_period(row["period"]),
            "amount": round(float(row["Expense"]), 2),
        }

    top_category = None
    if not categories.empty:
        row = categories.iloc[0]
        top_category = {
            "name": row["category"],
            "amount": round(float(row["total_amount"]), 2),
            "share": round(float(row["share_of_expenses"]), 2),
        }

    dominant_payment_method = None
    if not payment_methods.empty:
        row = payment_methods.iloc[0]
        dominant_payment_method = {
            "name": row["payment_method"],
            "amount": round(float(row["total_amount"]), 2),
            "share": round(float(row["share_of_expenses"]), 2),
        }

    amount_band = "Unknown"
    if "amount_band" in data and not data.empty and not data["amount_band"].dropna().empty:
        amount_band = str(data["amount_band"].mode().iloc[0])

    return {
        "metrics": metrics,
        "negative_net_savings_months": int(monthly["net_savings"].lt(0).sum())
        if not monthly.empty
        else 0,
        "positive_net_savings_months": int(monthly["net_savings"].gt(0).sum())
        if not monthly.empty
        else 0,
        "total_months": int(len(monthly)),
        "top_category": top_category,
        "highest_expense_month": highest_expense_month,
        "top_three_category_concentration": extended_metrics["top_three_category_concentration"],
        "category_count": int(len(categories)),
        "dominant_payment_method": dominant_payment_method,
        "outlier_count": outlier_sensitivity["outliers_capped"],
        "outlier_rate": outlier_sensitivity["outlier_transaction_rate"],
        "amount_band": amount_band,
        "income_count": int(data["transaction_type"].eq("Income").sum()),
        "expense_count": int(data["transaction_type"].eq("Expense").sum()),
    }


def generate_key_insights(analysis_results: AnalysisResults) -> list[str]:
    metrics = analysis_results["metrics"]
    top_category = analysis_results["top_category"]
    highest_expense_month = analysis_results["highest_expense_month"]
    dominant_payment_method = analysis_results["dominant_payment_method"]

    insights = [
        (
            f"Overall cash flow shows total income of {_format_money(metrics['total_income'])} "
            f"and total expenses of {_format_money(metrics['total_expense'])}, resulting in "
            f"net savings of {_format_money(metrics['net_savings'])} and a savings rate of "
            f"{metrics['savings_rate']:,.2f}%. "
            f"{analysis_results['negative_net_savings_months']} of "
            f"{analysis_results['total_months']} month(s) recorded negative net savings, "
            "which shows how often expenses exceeded income during the analyzed period."
        )
    ]

    if top_category:
        insights.append(
            f"{top_category['name']} is the largest expense category, accounting for "
            f"{top_category['share']:,.2f}% of total expenses. This makes it the most "
            "important category to review when identifying possible spending reductions."
        )

    if analysis_results["category_count"]:
        insights.append(
            "Expenses are concentrated across the largest categories. The top three "
            f"expense categories represent "
            f"{analysis_results['top_three_category_concentration']:,.2f}% of total "
            "expenses, which means budget control should focus on the categories with "
            "the largest shares before smaller spending areas."
        )

    if highest_expense_month:
        insights.append(
            f"{highest_expense_month['period']} recorded the highest monthly expenses "
            f"at {_format_money(highest_expense_month['amount'])}. This pattern may "
            "reflect seasonal spending, a one-time purchase, or recurring expenses that "
            "were higher than usual in that period."
        )

    if dominant_payment_method:
        insights.append(
            f"{dominant_payment_method['name']} is the dominant expense payment method, "
            f"representing {dominant_payment_method['share']:,.2f}% of total expenses. "
            "This indicates that payment-method behavior is relevant when reviewing how "
            "spending is distributed across categories."
        )

    insights.append(
        f"Most transactions fall within the {analysis_results['amount_band']} amount band, "
        f"and {analysis_results['outlier_count']} transaction(s) were flagged as outliers "
        f"({analysis_results['outlier_rate']:,.2f}% of cleaned records). The dataset also "
        f"contains {analysis_results['expense_count']} expense records and "
        f"{analysis_results['income_count']} income records, which shows the transaction "
        "mix available for interpretation."
    )

    return insights[:6]


def generate_recommendations(analysis_results: AnalysisResults) -> list[str]:
    metrics = analysis_results["metrics"]
    top_category = analysis_results["top_category"]
    highest_expense_month = analysis_results["highest_expense_month"]
    dominant_payment_method = analysis_results["dominant_payment_method"]

    recommendations = [
        (
            "Monitor monthly cash flow by reviewing months where expenses exceed income. "
            "Use the monthly trend chart to identify whether negative savings are caused "
            "by recurring expenses, seasonal spending, or one-time transactions."
        ),
        (
            "Prioritize the top spending categories before reducing smaller expenses. "
            f"Since the top three categories represent "
            f"{analysis_results['top_three_category_concentration']:,.2f}% of total "
            "expenses, small reductions in these areas can have a stronger effect on "
            "overall spending."
        ),
    ]

    if top_category:
        recommendations.append(
            f"Review {top_category['name']} transactions and set a category budget if "
            f"the {top_category['share']:,.2f}% expense share is higher than expected."
        )

    if highest_expense_month:
        recommendations.append(
            f"Filter {highest_expense_month['period']} transactions and review the "
            "largest entries to determine whether the peak spending came from recurring "
            "bills, seasonal activity, or one-time purchases."
        )

    if dominant_payment_method:
        recommendations.append(
            f"Group {dominant_payment_method['name']} transactions by category to "
            "determine whether this payment method is mainly linked to discretionary "
            "expenses, fixed expenses, or mixed spending."
        )

    if analysis_results["outlier_count"]:
        recommendations.append(
            "Validate flagged outlier transactions before final interpretation. Outliers "
            "may represent valid large purchases, but they may also include unusual "
            "entries or data issues that affect summary totals."
        )

    if metrics["net_savings"] < 0:
        recommendations.append(
            "Set a monthly savings target and compare actual net savings against that "
            "target after each period to track whether the negative savings pattern is "
            "improving."
        )

    return recommendations[:6]


def generate_conclusion(analysis_results: AnalysisResults) -> str:
    metrics = analysis_results["metrics"]
    top_category = analysis_results["top_category"]
    highest_expense_month = analysis_results["highest_expense_month"]
    dominant_payment_method = analysis_results["dominant_payment_method"]

    pattern_parts = [
        f"net savings of {_format_money(metrics['net_savings'])}",
        f"a savings rate of {metrics['savings_rate']:,.2f}%",
    ]
    if top_category:
        pattern_parts.append(f"{top_category['name']} as the largest expense category")
    if highest_expense_month:
        pattern_parts.append(f"{highest_expense_month['period']} as the peak spending month")
    if dominant_payment_method:
        pattern_parts.append(
            f"{dominant_payment_method['name']} as the dominant payment method"
        )

    return (
        "The Personal Finance Analytics System successfully transformed raw transaction "
        "records into cleaned financial summaries, visualizations, and dashboard insights. "
        f"The descriptive results identified {', '.join(pattern_parts)}, along with "
        f"{analysis_results['outlier_count']} flagged outlier transaction(s) and "
        f"{analysis_results['negative_net_savings_months']} month(s) with negative net "
        "savings. Overall, the dashboard is useful for financial monitoring because it "
        "shows where money is spent, which periods need attention, and which categories "
        "or payment methods should be reviewed first. These findings should be interpreted "
        "as descriptive results based on the available dataset, not as absolute proof of "
        "long-term financial behavior. Future improvements could include drill-down views, "
        "budget alerts, forecasting, and automated category recommendations."
    )


def generate_dashboard_summary(analysis_results: AnalysisResults) -> DashboardSummary:
    return {
        "key_insights": generate_key_insights(analysis_results),
        "recommendations": generate_recommendations(analysis_results),
        "conclusion": generate_conclusion(analysis_results),
        "charts": generate_chart_summaries(analysis_results),
    }


def generate_chart_summaries(analysis_results: AnalysisResults) -> dict[str, dict[str, str]]:
    metrics = analysis_results["metrics"]
    top_category = analysis_results["top_category"]
    highest_expense_month = analysis_results["highest_expense_month"]
    dominant_payment_method = analysis_results["dominant_payment_method"]

    summaries = {
        "monthly_trends": {
            "key_insight": (
                f"Overall cash flow shows total income of {_format_money(metrics['total_income'])} "
                f"and total expenses of {_format_money(metrics['total_expense'])}, resulting in "
                f"net savings of {_format_money(metrics['net_savings'])} and a savings rate of "
                f"{metrics['savings_rate']:,.2f}%. "
                f"{analysis_results['negative_net_savings_months']} of "
                f"{analysis_results['total_months']} month(s) recorded negative net savings."
            ),
            "recommendation": (
                "The user should monitor monthly cash flow more consistently, especially "
                "in months where expenses exceed income. Since "
                f"{analysis_results['negative_net_savings_months']} months recorded "
                "negative net savings, the user should review those months and identify "
                "whether the negative savings were caused by recurring bills, seasonal "
                "spending, or one-time transactions. A monthly savings target should "
                "also be set so the user can compare actual savings against a planned goal."
            ),
            "conclusion": _monthly_trend_conclusion(analysis_results),
        },
        "expense_share_by_category": {
            "key_insight": (
                "Expenses are concentrated across the largest categories. The top three "
                f"expense categories represent "
                f"{analysis_results['top_three_category_concentration']:,.2f}% of total "
                "expenses."
            ),
            "recommendation": (
                "The user should focus first on the top three expense categories because "
                f"they represent {analysis_results['top_three_category_concentration']:,.2f}% "
                "of total expenses. Instead of reducing all categories equally, the user "
                "should target the categories with the largest shares, since small reductions "
                "in these areas can have a stronger effect on total spending. Smaller "
                "categories may be monitored, but they should not be the first priority."
            ),
            "conclusion": _expense_share_conclusion(analysis_results),
        },
        "transaction_amount_distribution": {
            "key_insight": (
                f"Most transactions fall within the {analysis_results['amount_band']} amount "
                f"band, and {analysis_results['outlier_count']} transaction(s) were flagged "
                f"as outliers ({analysis_results['outlier_rate']:,.2f}% of cleaned records)."
            ),
            "recommendation": (
                f"The user should review the {analysis_results['outlier_count']} flagged "
                "outlier transactions before making final financial conclusions. These "
                "transactions may be valid large expenses, but they may also include unusual "
                "entries or data issues. Reviewing outliers can help confirm whether the "
                "total expenses and average transaction values accurately represent the "
                "user's normal spending behavior."
            ),
            "conclusion": _amount_distribution_conclusion(analysis_results),
        },
    }

    if top_category:
        summaries["top_expense_categories"] = {
            "key_insight": (
                f"{top_category['name']} is the largest expense category, accounting for "
                f"{top_category['share']:,.2f}% of total expenses."
            ),
            "recommendation": (
                f"The user should prioritize reviewing the {top_category['name']} category "
                f"because it is the largest expense category, accounting for "
                f"{top_category['share']:,.2f}% of total expenses. "
                f"{top_category['name']} transactions should be checked to determine "
                "whether they are essential, recurring, or discretionary. If many "
                f"{top_category['name']} expenses are non-essential, the user should set "
                "a monthly or quarterly budget limit for this category."
            ),
            "conclusion": _top_category_conclusion(analysis_results),
        }
    else:
        summaries["top_expense_categories"] = {
            "key_insight": "No expense records are available for category ranking.",
            "recommendation": "Validate expense classifications before reviewing category budgets.",
            "conclusion": (
                "The top expense category chart cannot identify a leading spending area "
                "because no expense records are available for category ranking."
            ),
        }

    if highest_expense_month:
        summaries["monthly_trends"]["key_insight"] += (
            f" {highest_expense_month['period']} recorded the highest monthly expenses "
            f"at {_format_money(highest_expense_month['amount'])}."
        )

    if dominant_payment_method:
        summaries["payment_method_expenses"] = {
            "key_insight": (
                f"{dominant_payment_method['name']} is the dominant expense payment method, "
                f"representing {dominant_payment_method['share']:,.2f}% of total expenses."
            ),
            "recommendation": (
                f"The user should monitor {dominant_payment_method['name']} spending closely "
                f"because it represents {dominant_payment_method['share']:,.2f}% of total "
                f"expenses. {dominant_payment_method['name']} transactions should be grouped "
                "by category to identify whether they are mostly connected to Travel, Food "
                "& Drink, Entertainment, or other discretionary expenses. Setting a monthly "
                f"{dominant_payment_method['name'].lower()} spending limit can help prevent "
                "overspending through this payment method."
            ),
            "conclusion": _payment_method_conclusion(analysis_results),
        }
    else:
        summaries["payment_method_expenses"] = {
            "key_insight": "No expense records are available for payment method analysis.",
            "recommendation": "Validate expense transactions and payment method values before interpreting payment behavior.",
            "conclusion": (
                "The payment method chart cannot identify a dominant spending method "
                "because no expense records are available for payment method analysis."
            ),
        }

    return summaries


def _monthly_trend_conclusion(analysis_results: AnalysisResults) -> str:
    highest_expense_month = analysis_results["highest_expense_month"]
    savings_phrase = (
        "Although there are months with positive net savings, the dashboard also shows that"
        if analysis_results["positive_net_savings_months"]
        else "The dashboard shows that"
    )
    peak_phrase = (
        f"The highest spending month was {highest_expense_month['period']}, with total "
        f"expenses of {_format_money(highest_expense_month['amount'])}. "
        if highest_expense_month
        else ""
    )

    return (
        "The monthly trend shows that the user's cash flow changes significantly across "
        f"the covered period. {savings_phrase} "
        f"{analysis_results['negative_net_savings_months']} months recorded negative net "
        "savings, meaning expenses exceeded income in several periods. "
        f"{peak_phrase}This indicates that monthly financial performance is not fully "
        "stable and should be reviewed regularly to identify periods of overspending."
    )


def _top_category_conclusion(analysis_results: AnalysisResults) -> str:
    top_category = analysis_results["top_category"]
    return (
        "The top expense categories show that spending is heavily concentrated in a few "
        f"areas. {top_category['name']} is the largest expense category, accounting for "
        f"{top_category['share']:,.2f}% of total expenses. This means that "
        f"{top_category['name']} has the strongest effect on overall spending compared "
        "with the other categories. Since a large portion of expenses comes from this "
        "category, it should be one of the main areas to review when planning a budget."
    )


def _expense_share_conclusion(analysis_results: AnalysisResults) -> str:
    return (
        "The expense share chart shows how total expenses are distributed across "
        "different categories. The top three expense categories represent "
        f"{analysis_results['top_three_category_concentration']:,.2f}% of total expenses "
        f"across {analysis_results['category_count']} categories, which means that "
        "spending is concentrated in a small number of areas rather than evenly spread "
        "across all categories. This suggests that budget improvements should focus "
        "first on the largest categories, because changes in those areas would have the "
        "greatest effect on total expenses."
    )


def _amount_distribution_conclusion(analysis_results: AnalysisResults) -> str:
    return (
        "The transaction amount distribution shows that most transactions fall within "
        f"the {analysis_results['amount_band']} amount band, while "
        f"{analysis_results['outlier_count']} transactions were flagged as outliers. "
        "This means that the dataset contains several unusually large transactions that "
        "may affect totals, averages, and spending patterns. These outlier transactions "
        "should be reviewed before making final financial conclusions, because they may "
        "represent valid large expenses or possible data issues."
    )


def _payment_method_conclusion(analysis_results: AnalysisResults) -> str:
    dominant_payment_method = analysis_results["dominant_payment_method"]
    return (
        f"The payment method chart shows that {dominant_payment_method['name']} is the "
        "most used payment method by expense total, representing "
        f"{dominant_payment_method['share']:,.2f}% of total expenses. This indicates "
        f"that a large share of spending is connected to "
        f"{dominant_payment_method['name'].lower()} transactions. Since "
        f"{dominant_payment_method['name'].lower()} spending makes up the biggest "
        "portion of payment-based expenses, it should be monitored closely and compared "
        "with the categories where it is most frequently used."
    )


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


def _format_money(value: object) -> str:
    return f"{float(value):,.2f}"


def _format_period(period: str) -> str:
    parsed = pd.Period(period, freq="M")
    return parsed.strftime("%B %Y")


def _to_html(figure, include_plotlyjs: bool = False) -> str:
    figure.update_layout(
        template="plotly_white",
        margin=dict(l=46, r=24, t=16, b=42),
        font=dict(family='Inter, "Segoe UI", sans-serif', color="#3d4947"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=CHART_PALETTE,
    )
    figure.update_xaxes(gridcolor="#f1f5f3", linecolor="#bcc9c6", zerolinecolor="#bcc9c6")
    figure.update_yaxes(gridcolor="#f1f5f3", linecolor="#bcc9c6", zerolinecolor="#bcc9c6")
    return figure.to_html(
        full_html=False,
        include_plotlyjs=include_plotlyjs,
        default_height="360px",
        config={"responsive": True},
    )
