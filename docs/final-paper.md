# Personal Finance Analytics System: Data Cleaning, Visualization, and Spending Insights

## 1. Title Page

**Project Title:** Personal Finance Analytics System: Data Cleaning, Visualization, and Spending Insights

**Course:** INTE 202 - Integrative Programming and Technologies

**Project Type:** Real-Life Data Analytics System using Python

**Student Name:** [Your Name]

**Section:** [Your Section]

**Instructor:** [Instructor Name]

**Date Submitted:** [Submission Date]

## 2. Introduction

Personal finance monitoring is important because income and expense records can quickly become difficult to understand when they are stored only as raw transaction logs. A user may know that money was spent, but without proper analysis, it is harder to identify spending patterns, high-expense categories, payment behavior, unusual transactions, and savings performance.

This project presents a Python-based Personal Finance Analytics System that loads a transaction dataset, cleans data quality issues, computes financial summaries, generates visualizations, and displays insights through a web dashboard. The system supports practical financial review by transforming raw records into understandable summaries and charts.

## 3. Problem Statement

Many individuals record income and expenses but do not have a simple way to analyze the information. Raw transaction datasets may contain missing values, inconsistent labels, invalid dates, duplicate rows, invalid amounts, and outliers. These issues can produce inaccurate results if the data is used directly.

The problem addressed by this project is the need for a data analytics system that can clean personal finance transaction data and convert it into useful financial insights. The system should help users understand how much they earn, how much they spend, which categories consume the most money, how expenses change over time, and which payment methods are used most often.

## 4. Objectives

The objectives of this project are:

- To load a personal finance transaction dataset from a CSV file.
- To clean and preprocess raw transaction records.
- To handle missing values, duplicates, invalid records, inconsistent text values, and outliers.
- To create additional analytics fields such as month, quarter, signed amount, amount band, and outlier flag.
- To compute descriptive statistics and financial metrics.
- To compute advanced validation metrics such as positive-savings months, category concentration, and flagged transaction rate.
- To generate charts for category, trend, share, distribution, and payment method analysis.
- To present results in a Flask web dashboard.
- To provide findings and recommendations based on the analyzed data.

## 5. Dataset Description

The dataset used in this project is a personal finance transaction dataset. It contains records of income and expense transactions from January 2, 2020 to December 29, 2024. The raw project dataset contains 1,505 rows and 6 source attributes.

### Raw Dataset Attributes

| Attribute | Description |
| --- | --- |
| Date | Calendar date when the transaction occurred. |
| Transaction Description | Short text description of the transaction. |
| Category | Category assigned to the transaction, such as Food & Drink, Rent, Travel, or Salary. |
| Amount | Transaction value before cleaning. |
| Type | Transaction classification, either Income or Expense. |
| Payment Method | Payment method used, such as Cash, Credit Card, Debit Card, Bank Transfer, or E-Wallet. |

### Cleaned Dataset Attributes

After preprocessing, the dataset contains 1,494 rows and 14 attributes. Additional fields were added for analysis:

| Attribute | Description |
| --- | --- |
| is_outlier | Indicates whether the amount exceeded the IQR threshold for its transaction type. |
| year | Transaction year. |
| month | Transaction month number. |
| month_name | Transaction month name. |
| period | Year-month value used for monthly trends. |
| quarter | Calendar quarter. |
| signed_amount | Income as a positive value and expense as a negative value. |
| amount_band | Transaction size group: Low, Medium, High, or Very High. |

## 6. Methodology

The project followed a data analytics workflow using Python. First, the system loaded the raw CSV file and checked that the required columns were available. Next, the dataset was cleaned by handling missing values, converting dates and amounts, removing invalid records, standardizing text fields, and removing duplicates. Unusually large values were flagged within income and expense records separately, but validated amounts were not modified.

After cleaning, the system engineered new columns to support analysis. These included time-based fields for monthly and quarterly grouping, a signed amount field for net savings analysis, an outlier flag, and transaction amount bands.

The cleaned dataset was then analyzed using descriptive statistics, category summaries, monthly summaries, payment method summaries, an outlier audit, semantic category auditing, and financial metrics. Finally, the results were displayed in a Flask dashboard with Plotly visualizations, summary tables, data preview, generated insights, and cleaned CSV export.

## 7. Data Cleaning Process

The raw dataset contained realistic data quality issues that needed to be fixed before analysis. The cleaning process included the following steps:

- Renamed source columns into consistent lowercase field names.
- Filled missing text values with `Unknown`.
- Standardized category, transaction type, and payment method values.
- Removed duplicate transaction records.
- Converted valid date values into date format.
- Removed rows with invalid dates.
- Converted amount values into numeric format after removing formatting characters such as currency symbols and commas.
- Removed invalid, missing, zero, and negative amount values.
- Removed records with invalid transaction types.
- Flagged high outlier amounts using separate interquartile-range thresholds for income and expense records without changing their values.
- Added engineered columns for analysis.

### Cleaning Summary

| Cleaning Item | Result |
| --- | ---: |
| Original rows | 1,505 |
| Cleaned rows | 1,494 |
| Removed rows | 11 |
| Missing values filled | 2 |
| Duplicate rows removed | 5 |
| Invalid amount rows removed | 3 |
| Invalid date rows removed | 2 |
| Invalid transaction type rows removed | 1 |
| Standardized text entries | 5 |
| Outliers flagged | 6 |

## 8. Data Analysis and Computations

The cleaned dataset was analyzed to compute financial totals, transaction statistics, category rankings, payment method summaries, and monthly trends.

### Key Financial Metrics

| Metric | Value |
| --- | ---: |
| Total transactions | 1,494 |
| Total income | 1,059,279.52 |
| Total expenses | 820,414.15 |
| Net savings | 238,865.37 |
| Savings rate | 22.55% |
| Average transaction | 1,258.16 |
| Median transaction | 953.08 |
| Largest transaction | 4,345.50 |

### Descriptive Statistics

| Metric | Value |
| --- | ---: |
| Mean | 1,258.16 |
| Median | 953.08 |
| Mode | 1,367.57 |
| Standard deviation | 1,059.60 |
| Minimum | 92.58 |
| Maximum | 4,345.50 |

### Top Expense Categories

| Category | Total Amount | Transaction Count | Share of Expenses |
| --- | ---: | ---: | ---: |
| Travel | 220,293.70 | 158 | 26.85% |
| Rent | 210,387.81 | 165 | 25.64% |
| Entertainment | 80,864.31 | 142 | 9.86% |
| Food & Drink | 73,075.51 | 149 | 8.91% |
| Utilities | 65,936.86 | 156 | 8.04% |

### Top Expense Payment Methods

| Payment Method | Total Amount | Transaction Count | Share of Expenses |
| --- | ---: | ---: | ---: |
| Credit Card | 284,266.18 | 262 | 34.65% |
| Bank Transfer | 276,324.67 | 321 | 33.68% |
| Debit Card | 156,801.04 | 274 | 19.11% |
| E-Wallet | 80,346.08 | 141 | 9.79% |
| Cash | 22,157.95 | 71 | 2.70% |
| Unknown | 518.23 | 1 | 0.06% |

### Advanced Validation Metrics

| Metric | Value |
| --- | ---: |
| Monthly net cash-flow variance | 61,183,537.73 |
| Monthly net cash-flow standard deviation | 7,821.99 |
| Positive savings months | 36 of 60 |
| Positive savings month share | 60.00% |
| Top three category concentration | 62.35% |
| Flagged transaction rate | 0.40% |
| Expense mean-median gap | 132.07 |

### Outlier Audit

The system applies the IQR rule separately to income and expense records. It flags unusual values for review while preserving every validated transaction amount for financial calculations.

| Metric | Value |
| --- | ---: |
| Flagged transactions | 6 |
| Flagged transaction rate | 0.40% |
| Flagged income transactions | 0 |
| Flagged expense transactions | 6 |
| Flagged total amount | 15,269.81 |
| Largest flagged amount | 2,913.06 |
| Top flagged category | Travel |

The audit identifies unusual transactions without treating them as errors or changing totals. Each flagged record should be reviewed in context before any correction is made.

## 9. Visualizations

The dashboard includes the following visualizations:

### Bar Graph: Top Expense Categories

This chart shows which categories have the highest total expenses. It helps identify the areas where spending is most concentrated.

### Line Graph: Monthly Income, Expenses, and Net Savings

This chart shows financial movement over time. It compares monthly income, monthly expenses, and net savings, making it easier to detect months with high spending or poor savings performance.

### Pie Chart: Expense Share by Category

This chart shows the percentage contribution of each major expense category. It helps communicate how total expenses are distributed across categories.

### Histogram: Transaction Amount Distribution

This chart shows how transaction amounts are distributed. It helps reveal whether most transactions are small, medium, high, or very high.

### Bar Graph: Expense Totals by Payment Method

This chart compares expense totals across payment methods. It helps identify whether spending is mostly done through credit card, debit card, bank transfer, e-wallet, cash, or unknown payment methods.

The dashboard also includes supporting tables for statistical computations, top expense categories, monthly summaries, payment methods, cleaning results, advanced validation metrics, an outlier audit, semantic category audit, and a cleaned data preview.

## 10. Findings and Insights

The analysis produced several important findings:

- The cleaned dataset contains 1,494 valid transaction records after removing duplicates and invalid rows.
- Total income exceeds total expenses, resulting in net savings of 238,865.37.
- The savings rate is 22.55% across the full dataset period.
- Travel is the largest expense category, accounting for 26.85% of total expenses.
- The highest spending month is January 2023, with 23,267.92 in expenses.
- The dataset contains 1,070 expense records and 424 income records.
- Credit Card is the highest expense payment method, representing 34.65% of spending.
- 36 of 60 months, or 60.00%, show positive savings.
- The top three expense categories represent 62.35% of total expenses.
- Six expense transactions are flagged for review; their original values remain unchanged in all calculations.

These findings show positive aggregate savings alongside substantial month-to-month variation. Expenses are concentrated primarily in Travel and Rent, so those categories have the greatest influence on overall spending.

## 11. Conclusion

The Personal Finance Analytics System successfully transforms raw transaction records into a cleaned and analytics-ready dataset. The system handles common data quality issues, computes financial metrics, creates useful visualizations, and presents insights through a web dashboard.

Based on the analysis, total income is greater than total expenses, resulting in positive net savings across the full period, although 24 individual months have negative net savings. The project demonstrates how Python, pandas, Plotly, and Flask can be used together to build a practical data analytics system for personal finance decision-making. Results remain descriptive findings from the available dataset, and flagged transactions require contextual review rather than automatic modification.

## 12. Recommendations

The following recommendations are based on the analysis:

- Set budget limits for high-spending categories, especially Travel, Rent, Food & Drink, and Entertainment.
- Review months with unusually high expenses, especially January 2023, to identify what caused the increase.
- Monitor credit card spending closely because it is the highest expense payment method.
- Maintain a monthly savings target and investigate the 24 months with negative net savings.
- Continue cleaning and validating transaction data before performing analysis.
- Review outlier transactions regularly to determine whether they are valid large expenses or data entry issues.
- Use the dashboard regularly to compare income, expenses, and savings trends over time.

## 13. References

- Project dataset: `data/raw/raw_personal_finance_dataset.csv`
- Cleaned dataset audit: `docs/data-dictionary-and-audit.md`
- Python Software Foundation. Python programming language. https://www.python.org/
- pandas development team. pandas documentation. https://pandas.pydata.org/
- Plotly Technologies Inc. Plotly Python documentation. https://plotly.com/python/
- Pallets Projects. Flask documentation. https://flask.palletsprojects.com/
- pytest documentation. https://docs.pytest.org/
