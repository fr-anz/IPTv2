# Personal Finance Analytics System

A Flask dashboard for cleaning, analyzing, and visualizing personal finance transaction data from CSV files. The application loads the bundled dataset by default and also accepts compatible user uploads for interactive analysis.

## Features

- Cleans duplicate, missing, invalid, and inconsistently formatted records.
- Standardizes categories, transaction types, and payment methods.
- Reviews salary records classified as expenses and infers some unknown categories.
- Preserves transaction amounts while flagging statistical outliers for review.
- Calculates income, expenses, net savings, savings rate, trends, and descriptive statistics.
- Builds interactive Plotly charts and plain-language financial insights.
- Displays cleaning, outlier, and category-semantic audit results.
- Exports the cleaned bundled dataset as CSV.

## Requirements

- Python 3.10 or later
- A PowerShell, Command Prompt, or POSIX-compatible terminal

The Python packages are listed in [`requirements.txt`](requirements.txt).

## Setup and Run

From the project root, create a virtual environment and install the dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

On macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

Open <http://127.0.0.1:5000> after the Flask development server starts.

## CSV Input Format

Uploaded CSV files must include these case-sensitive columns:

| Column | Required | Description |
| --- | :---: | --- |
| `Date` | Yes | Transaction date; values that cannot be parsed are removed. |
| `Transaction Description` | Yes | Description used for display and category inference. |
| `Category` | Yes | Transaction category. |
| `Amount` | Yes | Positive numeric amount; currency symbols and commas are accepted. |
| `Type` | Yes | Transaction type: `Income` or `Expense`. |
| `Payment Method` | No | Payment method; omitted or blank values become `Unknown`. |

The default input is [`data/raw/raw_personal_finance_dataset.csv`](data/raw/raw_personal_finance_dataset.csv). Uploaded files are analyzed in the dashboard for the current request; the **Download Cleaned CSV** action exports a cleaned copy of the bundled default dataset.

## Export a Cleaned Dataset

Clean the bundled dataset and write the result to `data/processed/cleaned_personal_finance_dataset.csv`:

```powershell
python scripts\clean_dataset.py
```

Use another source or destination with the optional arguments:

```powershell
python scripts\clean_dataset.py --input path\to\transactions.csv --output path\to\cleaned.csv
```

## Run Tests

```powershell
python -m pytest
```

## Project Structure

```text
.
|-- app.py                     # Flask application and routes
|-- finance_analytics/
|   |-- analytics.py           # Metrics, summaries, charts, and insights
|   `-- data.py                # CSV validation and cleaning pipeline
|-- data/
|   |-- raw/                   # Bundled source dataset
|   `-- processed/             # Generated cleaned datasets
|-- scripts/clean_dataset.py   # Command-line CSV cleaning utility
|-- static/css/styles.css      # Dashboard styling
|-- templates/                 # Flask/Jinja templates
|-- tests/test_analytics.py    # Cleaning, analytics, and dashboard tests
`-- docs/                      # Data audit and project paper material
```

## Notes

- Generated files under `data/processed/` are not committed to the repository.
- `python app.py` runs Flask's development server and is intended for local use.
