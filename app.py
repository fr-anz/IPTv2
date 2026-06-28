from __future__ import annotations

from io import BytesIO
from pathlib import Path

from flask import Flask, flash, render_template, request, send_file

from finance_analytics.analytics import (
    build_dashboard_analysis_results,
    build_dashboard_charts,
    calculate_extended_metrics,
    calculate_metrics,
    generate_all_insights,
    generate_dashboard_summary,
    get_category_summary,
    get_category_semantic_audit,
    get_monthly_summary,
    get_outlier_audit,
    get_payment_method_summary,
    get_statistics_table,
)
from finance_analytics.data import clean_transactions, load_transactions


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = BASE_DIR / "data" / "raw" / "raw_personal_finance_dataset.csv"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"

    @app.route("/", methods=["GET", "POST"])
    def dashboard():
        raw_data, source_name = _read_selected_dataset()
        cleaned_data, cleaning_report = clean_transactions(raw_data)

        metrics = calculate_metrics(cleaned_data)
        charts = build_dashboard_charts(cleaned_data)
        chart_insights = generate_all_insights(cleaned_data, metrics)
        insights = chart_insights["overall_summary"]
        analysis_results = build_dashboard_analysis_results(cleaned_data, metrics)
        dashboard_summary = generate_dashboard_summary(analysis_results)
        monthly_summary = get_monthly_summary(cleaned_data).tail(12)
        category_summary = get_category_summary(cleaned_data).head(10)
        payment_method_summary = get_payment_method_summary(cleaned_data)
        statistics_table = get_statistics_table(cleaned_data)
        extended_metrics = calculate_extended_metrics(cleaned_data)
        outlier_audit = get_outlier_audit(cleaned_data)
        semantic_audit = get_category_semantic_audit(cleaned_data)

        return render_template(
            "dashboard.html",
            source_name=source_name,
            metrics=metrics,
            charts=charts,
            insights=insights,
            chart_insights=chart_insights,
            dashboard_summary=dashboard_summary,
            cleaning_report=cleaning_report,
            monthly_summary=monthly_summary.to_dict("records"),
            category_summary=category_summary.to_dict("records"),
            payment_method_summary=payment_method_summary.to_dict("records"),
            statistics_table=statistics_table.to_dict("records"),
            extended_metrics=extended_metrics,
            outlier_audit=outlier_audit,
            semantic_audit=semantic_audit,
            cleaned_preview=cleaned_data.head(25).to_dict("records"),
            columns=cleaned_data.columns,
        )

    @app.get("/download-cleaned")
    def download_cleaned_dataset():
        raw_data = load_transactions(DEFAULT_DATASET)
        cleaned_data, _ = clean_transactions(raw_data)

        output = BytesIO()
        cleaned_data.to_csv(output, index=False)
        output.seek(0)

        return send_file(
            output,
            mimetype="text/csv",
            as_attachment=True,
            download_name="cleaned_personal_finance_dataset.csv",
        )

    return app


def _read_selected_dataset():
    uploaded_file = request.files.get("dataset")
    if uploaded_file and uploaded_file.filename:
        try:
            return load_transactions(uploaded_file), uploaded_file.filename
        except ValueError as exc:
            flash(str(exc), "error")

    return load_transactions(DEFAULT_DATASET), DEFAULT_DATASET.name


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
