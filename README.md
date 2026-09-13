# credit-scoring-risk-analysis
Automated Python ETL pipeline, SQL risk analysis, and interactive BI dashboard evaluating loan approvals and default risk on 20,000 credit applications.
# Credit Scoring & Risk Analysis in Lending

An end-to-end data analytics and credit risk assessment project modeling 20,000 synthetic loan applications across seven UK regions (Apr 2023 – Apr 2025).

## Project Overview
* **Phase 0 — Python Data Pipeline (ETL):** Automated four-stage ETL (`extract`, `transform`, `validate`, `save`) in `credit_pipeline.py` enforcing data-quality checks, FICO banding, and debt-to-income (DTI) metrics.
* **Phase 1 — Exploratory Data Analysis (EDA):** Evaluated portfolio distributions across credit scores, applicant income bands, and employment tenure.
* **Phase 2 — SQL Risk Analysis:** Structured SQL queries in `phase2_sql_queries.sql` evaluating loan purpose demand, regional approval rates, default likelihood, and risk classifications.
* **Phase 3 — BI Dashboard:** Interactive front-end risk dashboard in `dashboard.html` with real-time filtering by region, credit risk tier, and employment tenure.

## Repository Contents
* `credit_pipeline.py` - ETL pipeline script.
* `cleaned_credit_data.csv` - Validated, feature-engineered dataset.
* `credit_analysis.db` - Indexed SQLite database.
* `phase2_sql_queries.sql` - Standalone SQL queries for risk assessment.
* `dashboard.html` - Interactive lending risk dashboard.
* `Credit_Scoring_Project_Report.docx` - Full technical report and methodology.
