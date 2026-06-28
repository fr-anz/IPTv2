# Personal Finance Analytics System

A Flask web application that cleans and analyzes personal finance transaction data from a CSV file.

The application displays income, expenses, savings, monthly trends, category summaries, descriptive statistics, charts, and data-quality findings in a dashboard. It can use the included dataset or a CSV uploaded by the user.

## What It Does

- Cleans missing, duplicate, invalid, and inconsistently formatted records.
- Reviews `Salary` records marked as `Expense` and automatically corrects their classification.
- Calculates financial totals, averages, savings, trends, and category rankings.
- Flags unusual transactions without removing them.
- Generates interactive charts and a preview of the cleaned data.
- Allows the cleaned dataset to be downloaded as a CSV file.

## Run the Application

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

## Other Commands

Export the cleaned dataset:

```powershell
python scripts\clean_dataset.py
```

Run the tests:

```powershell
python -m pytest
```
