# Final Paper Outline

## 1. Title Page

Personal Finance Analytics System using Python

## 2. Introduction

Explain why personal expense monitoring is useful for students, households, or small teams that need to understand spending behavior.

## 3. Problem Statement

Users often record income and expenses but do not easily see spending patterns, savings trends, outliers, or categories that need attention.

## 4. Objectives

- Load and clean a personal finance transaction dataset.
- Compute descriptive statistics and financial summaries.
- Visualize income, expenses, category shares, and transaction distributions.
- Generate data-supported insights and recommendations.

## 5. Dataset Description

Describe the raw project dataset as a personal finance transaction dataset containing transaction date, description, category, amount, transaction type, and payment method. Include the data dictionary and before/after dataset audit from `docs/data-dictionary-and-audit.md`. The preprocessing step also adds analytics attributes such as period, quarter, signed amount, outlier flag, and amount band.

## 6. Methodology

Describe the workflow: load CSV, validate required columns, clean records, engineer features, compute summaries, create charts, and present findings in the web dashboard.

## 7. Data Cleaning Process

Document missing value handling, duplicate removal, category/type/payment method standardization, currency amount conversion, date conversion, invalid amount filtering, invalid date filtering, invalid type filtering, and outlier capping. Present the issues as data quality findings from the raw project dataset.

## 8. Data Analysis and Computations

Include totals, averages, median, mode, standard deviation, minimum, maximum, monthly trends, and category rankings.

## 9. Visualizations

- Bar graph: top expense categories
- Line graph: monthly income, expenses, and net savings
- Pie chart: expense share by category
- Histogram: transaction amount distribution
- Additional bar graph: expense totals by payment method

## 10. Findings and Insights

Use the dashboard insights as the starting point, then explain what the values mean for financial decision-making.

## 11. Conclusion

Summarize how the system helps monitor personal finance behavior.

## 12. Recommendations

Recommend budget limits for high-spending categories, monthly savings targets, and regular review of unusual transactions.

## 13. References

List dataset source, Python libraries, and any external references used in the final paper.
