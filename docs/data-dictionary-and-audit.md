# Data Dictionary and Dataset Audit

## Dataset Overview

The project uses a personal finance transaction dataset for analyzing income, expenses, spending categories, payment methods, monthly trends, and savings behavior. The raw project dataset contains 1,505 transaction records and 6 attributes. After cleaning and preprocessing, the analytics-ready dataset contains 1,494 records and 14 attributes.

## Raw Dataset Data Dictionary

| Attribute | Description | Data Type | Example Value | Notes |
| --- | --- | --- | --- | --- |
| Date | Calendar date when the transaction occurred. | Date/Text | 2020-01-02 | Converted to a valid date format during preprocessing. |
| Transaction Description | Short description of the transaction. | Text | Score each. | Missing or blank descriptions are filled during preprocessing. |
| Category | Transaction category. | Text | Food & Drink | Standardized for casing and spelling consistency. |
| Amount | Transaction value. | Numeric/Text | 1485.69 | Currency symbols, commas, invalid values, and non-positive values are handled during preprocessing. |
| Type | Transaction classification. | Text | Expense | Standardized to valid values: Income or Expense. |
| Payment Method | Method used for the transaction. | Text | Bank Transfer | Standardized into consistent payment method labels. |

## Cleaned Dataset Data Dictionary

| Attribute | Description | Data Type | Example Value | Purpose |
| --- | --- | --- | --- | --- |
| date | Cleaned transaction date. | Date | 2020-01-02 | Used for time-based analysis. |
| description | Cleaned transaction description. | Text | Score each. | Provides transaction context. |
| category | Standardized transaction category. | Text | Food & Drink | Used for category-level summaries and charts. |
| amount | Parsed transaction amount. | Numeric | 1485.69 | Authoritative validated value used in all financial calculations. |
| transaction_type | Standardized transaction type. | Text | Expense | Separates income and expense records. |
| payment_method | Standardized payment method. | Text | Bank Transfer | Used for payment behavior analysis. |
| is_outlier | Indicates whether the transaction exceeded the IQR threshold for its transaction type. | Boolean | False | Supports review without modifying the amount. |
| year | Transaction year. | Integer | 2020 | Supports yearly grouping. |
| month | Transaction month number. | Integer | 1 | Supports monthly sorting and grouping. |
| month_name | Transaction month name. | Text | January | Improves chart readability. |
| period | Year-month period. | Text | 2020-01 | Used for monthly trend analysis. |
| quarter | Calendar quarter. | Text | Q1 | Supports quarterly grouping. |
| signed_amount | Income as positive and expense as negative. | Numeric | -1485.69 | Used for net savings calculations. |
| amount_band | Transaction size group. | Text | High | Supports distribution analysis. |

## Before Cleaning Audit

| Audit Item | Result |
| --- | ---: |
| Total rows | 1,505 |
| Total attributes | 6 |
| Duplicate rows | 5 |
| Missing or blank descriptions | 3 |
| Missing or blank categories | 2 |
| Missing or blank payment methods | 11 |
| Invalid date rows | 2 |
| Invalid or non-positive amount rows | 3 |
| Invalid transaction type rows | 1 |
| Date range | 2020-01-02 to 2024-12-29 |
| Amount range before cleaning | -25.00 to 4,996.00 |

### Raw Data Quality Observations

The raw project dataset contained common data quality issues that required preprocessing before analysis. These included duplicate transaction records, blank text fields, inconsistent category casing, inconsistent payment method labels, invalid date values, invalid or non-positive transaction amounts, and a transaction type outside the accepted Income/Expense classification.

Observed category labels included both standardized and inconsistent forms, such as `Food & Drink`, `food & drink`, `Shopping`, `shopping`, `Utilities`, and `UTILITIES`. Observed payment method labels included variants such as `E-Wallet`, `ewallet`, `Credit Card`, `creditcard`, `Bank Transfer`, and `bank transfer`.

## After Cleaning Audit

| Audit Item | Result |
| --- | ---: |
| Total rows | 1,494 |
| Total attributes | 14 |
| Duplicate rows | 0 |
| Missing or blank values | 0 |
| Invalid date rows | 0 |
| Invalid or non-positive amount rows | 0 |
| Invalid transaction type rows | 0 |
| Date range | 2020-01-02 to 2024-12-29 |
| Validated amount range | 92.58 to 4,345.50 |

### Cleaned Data Quality Results

After preprocessing, the dataset was made suitable for analytics. Duplicate records were removed, missing text values were filled with `Unknown`, date values were parsed into a consistent date format, invalid dates were removed, amount values were converted to numeric format, invalid and non-positive amounts were removed, transaction types were standardized to `Income` and `Expense`, and payment methods were standardized into consistent labels.

The cleaned dataset also includes engineered analytics attributes for year, month, month name, monthly period, quarter, signed amount, a non-mutating outlier flag, and amount band. These fields support descriptive statistics, monthly trend analysis, category comparisons, payment method analysis, and dashboard visualizations.

## Standardized Values

| Field | Cleaned Values |
| --- | --- |
| transaction_type | Expense, Income |
| payment_method | Bank Transfer, Cash, Credit Card, Debit Card, E-Wallet, Unknown |
| category | Entertainment, Food & Drink, Groceries, Healthcare, Rent, Shopping, Transportation, Travel, Utilities |

## Preprocessing Summary

| Step | Purpose |
| --- | --- |
| Missing value handling | Filled missing text fields with `Unknown`. |
| Text standardization | Trimmed spaces and standardized casing for categories, transaction types, and payment methods. |
| Duplicate removal | Removed repeated transaction records. |
| Date validation | Converted valid dates and removed invalid date records. |
| Amount conversion | Removed formatting characters and converted values to numeric form. |
| Invalid amount filtering | Removed non-numeric, zero, and negative transaction amounts. |
| Transaction type validation | Kept only valid `Income` and `Expense` records. |
| Outlier review | Flagged high values using separate income and expense IQR thresholds without changing transaction amounts. |
| Feature engineering | Added time, signed amount, outlier, and amount band attributes. |
