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
- To compute advanced validation metrics such as positive-savings months, category concentration, flagged transaction rate, and outlier sensitivity.
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

After preprocessing, the dataset contains 1,494 rows and 15 attributes. Additional fields were added for analysis:

| Attribute | Description |
| --- | --- |
| amount_cleaned | Numeric amount after parsing and outlier capping. |
| is_outlier | Indicates whether the original amount exceeded the outlier threshold. |
| year | Transaction year. |
| month | Transaction month number. |
| month_name | Transaction month name. |
| period | Year-month value used for monthly trends. |
| quarter | Calendar quarter. |
| signed_amount | Income as a positive value and expense as a negative value. |
| amount_band | Transaction size group: Low, Medium, High, or Very High. |

## 6. Methodology

The project followed a data analytics workflow using Python. First, the system loaded the raw CSV file and checked that the required columns were available. Next, the dataset was cleaned by handling missing values, converting dates and amounts, removing invalid records, standardizing text fields, removing duplicates, and capping outliers.

After cleaning, the system engineered new columns to support analysis. These included time-based fields for monthly and quarterly grouping, a signed amount field for net savings analysis, an outlier flag, and transaction amount bands.

The cleaned dataset was then analyzed using descriptive statistics, category summaries, monthly summaries, payment method summaries, outlier sensitivity checks, semantic category auditing, and financial metrics. Finally, the results were displayed in a Flask dashboard with Plotly visualizations, summary tables, data preview, generated insights, and cleaned CSV export.

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
- Capped high outlier amounts using the interquartile range method.
- Added engineered columns for analysis.

### Cleaning Summary

| Cleaning Item | Result |
| --- | ---: |
| Original rows | 1,505 |
| Cleaned rows | 1,494 |
| Removed rows | 11 |
| Missing values filled | 16 |
| Duplicate rows removed | 5 |
| Invalid amount rows removed | 3 |
| Invalid date rows removed | 2 |
| Invalid transaction type rows removed | 1 |
| Standardized text entries | 30 |
| Outliers capped | 88 |

## 8. Data Analysis and Computations

The cleaned dataset was analyzed to compute financial totals, transaction statistics, category rankings, payment method summaries, and monthly trends.

### Key Financial Metrics

| Metric | Value |
| --- | ---: |
| Total transactions | 1,494 |
| Total income | 666,419.92 |
| Total expenses | 1,222,101.20 |
| Net savings | -555,681.28 |
| Savings rate | -83.38% |
| Average transaction | 1,264.07 |
| Median transaction | 1,157.37 |
| Largest transaction | 3,342.01 |

### Descriptive Statistics

| Metric | Value |
| --- | ---: |
| Mean | 1,264.07 |
| Median | 1,157.37 |
| Mode | 3,342.01 |
| Standard deviation | 851.74 |
| Minimum | 14.37 |
| Maximum | 3,342.01 |

### Top Expense Categories

| Category | Total Amount | Transaction Count | Share of Expenses |
| --- | ---: | ---: | ---: |
| Travel | 167,905.62 | 158 | 13.74% |
| Rent | 162,075.39 | 165 | 13.26% |
| Food & Drink | 159,820.00 | 149 | 13.08% |
| Entertainment | 148,141.88 | 142 | 12.12% |
| Salary | 147,997.42 | 145 | 12.11% |

### Top Expense Payment Methods

| Payment Method | Total Amount | Transaction Count | Share of Expenses |
| --- | ---: | ---: | ---: |
| Credit Card | 295,054.95 | 293 | 24.14% |
| Debit Card | 286,833.48 | 282 | 23.47% |
| Bank Transfer | 270,248.82 | 282 | 22.11% |
| E-Wallet | 242,901.26 | 231 | 19.88% |
| Cash | 117,555.35 | 118 | 9.62% |

### Advanced Validation Metrics

| Metric | Value |
| --- | ---: |
| Monthly net cash-flow variance | 60,378,473.53 |
| Monthly net cash-flow standard deviation | 7,770.36 |
| Positive savings months | 6 of 60 |
| Positive savings month share | 10.00% |
| Top three category concentration | 40.08% |
| Flagged transaction rate | 5.89% |
| Expense mean-median gap | 11.36 |

### Outlier Sensitivity

The system keeps both the parsed amount and the capped cleaned amount, allowing the dashboard to compare totals before and after outlier treatment.

| Metric | Before Capping | After Capping | Change |
| --- | ---: | ---: | ---: |
| Income | 735,593.04 | 666,419.92 | -69,173.12 |
| Expenses | 1,222,101.20 | 1,222,101.20 | 0.00 |
| Net savings | -486,508.16 | -555,681.28 | -69,173.12 |

The outlier sensitivity check shows that 88 transactions were capped, equal to 5.89% of cleaned records.

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

The dashboard also includes supporting tables for statistical computations, top expense categories, monthly summaries, payment methods, cleaning results, advanced validation metrics, outlier sensitivity, semantic category audit, and a cleaned data preview.

## 10. Findings and Insights

The analysis produced several important findings:

- The cleaned dataset contains 1,494 valid transaction records after removing duplicates and invalid rows.
- Total expenses are higher than total income, resulting in negative net savings of -555,681.28.
- The savings rate is -83.38%, showing that expenses exceeded income during the dataset period.
- Expenses are concentrated in Travel, which accounts for 13.74% of total expenses.
- The highest spending month is August 2020, with 31,937.82 in expenses.
- The dataset contains 1,215 expense records and 279 income records, meaning expenses have more transaction-level detail than income.
- Credit Card is the highest expense payment method, representing 24.14% of spending.
- Only 6 of 60 months, or 10.00%, show positive savings.
- The top three expense categories represent 40.08% of total expenses.
- Salary appears as an expense category in 145 records totaling 147,997.42, while Salary income records total 0. This is treated as a dataset semantic issue and is reported as-is rather than silently recoded.

These findings show that the user has a high expense load compared with income. The dashboard also shows that expenses are spread across several major categories, with Travel, Rent, Food & Drink, Entertainment, and Salary-related records appearing among the largest totals.

## 11. Conclusion

The Personal Finance Analytics System successfully transforms raw transaction records into a cleaned and analytics-ready dataset. The system handles common data quality issues, computes financial metrics, creates useful visualizations, and presents insights through a web dashboard.

Based on the analysis, the dataset shows that total expenses are greater than total income, resulting in negative net savings. This indicates that financial monitoring and budget planning are necessary. The project demonstrates how Python, pandas, Plotly, and Flask can be used together to build a practical data analytics system for personal finance decision-making. The results should still be interpreted as descriptive findings from the available dataset, especially because some category labels, such as Salary, require semantic review before making final behavioral conclusions.

## 12. Recommendations

The following recommendations are based on the analysis:

- Set budget limits for high-spending categories, especially Travel, Rent, Food & Drink, and Entertainment.
- Review months with unusually high expenses, such as August 2020, to identify what caused the increase.
- Monitor credit card spending closely because it is the highest expense payment method.
- Establish a monthly savings target to improve the negative savings rate.
- Continue cleaning and validating transaction data before performing analysis.
- Review outlier transactions regularly to determine whether they are valid large expenses or data entry issues.
- Review and correct ambiguous category labels, especially Salary records marked as expenses.
- Use the dashboard regularly to compare income, expenses, and savings trends over time.

## 13. References

- Project dataset: `data/raw/raw_personal_finance_dataset.csv`
- Cleaned dataset audit: `docs/data-dictionary-and-audit.md`
- Python Software Foundation. Python programming language. https://www.python.org/
- pandas development team. pandas documentation. https://pandas.pydata.org/
- Plotly Technologies Inc. Plotly Python documentation. https://plotly.com/python/
- Pallets Projects. Flask documentation. https://flask.palletsprojects.com/
- pytest documentation. https://docs.pytest.org/
