"""
Project 2: Credit Scoring & Risk Analysis in Lending
Phase 0 — Python Data Pipeline (ETL Setup)

Four-stage pipeline:
    extract_credit_data()    -> load raw applicant data
    transform_credit_data()  -> engineer features, fix dtypes
    validate_credit_data()   -> enforce data-quality rules
    save_credit_data()       -> persist cleaned data for SQL / BI use

Run directly:  python credit_pipeline.py
"""

import pandas as pd
import numpy as np
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("credit_pipeline")

RAW_PATH = Path("raw_credit_data.csv")
CLEAN_CSV_PATH = Path("cleaned_credit_data.csv")
CLEAN_DB_PATH = Path("credit_analysis.db")


# ---------------------------------------------------------------------------
# 1. EXTRACT
# ---------------------------------------------------------------------------
def extract_credit_data(path: Path = RAW_PATH) -> pd.DataFrame:
    """Load the raw applicant/loan dataset from CSV."""
    logger.info(f"Extracting data from {path} ...")
    df = pd.read_csv(path)
    logger.info(f"Extracted {len(df):,} rows, {len(df.columns)} columns.")
    return df


# ---------------------------------------------------------------------------
# 2. TRANSFORM
# ---------------------------------------------------------------------------
def transform_credit_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fix data types and engineer analysis-ready features:
      - application_date        -> datetime
      - categorical columns     -> category dtype
      - debt_to_income_ratio    -> monthly_expense / (annual_income / 12)
      - credit_risk_tier        -> standard FICO-style bands from credit_score
      - income_group            -> banded annual_income for group comparisons
      - approved_flag           -> 1/0 helper for approval-rate calculations
      - late_payment_band       -> grouped late_payments (0 / 1-2 / 3+)
    """
    df = df.copy()
    logger.info("Transforming data ...")

    # --- fix dtypes -----------------------------------------------------
    df["application_date"] = pd.to_datetime(df["application_date"], errors="coerce")

    categorical_cols = [
        "gender", "marital_status", "employment_status", "loan_purpose",
        "approval_status", "region",
    ]
    for col in categorical_cols:
        df[col] = df[col].astype("category")

    numeric_cols = [
        "age", "annual_income", "loan_amount", "loan_term_months", "credit_score",
        "existing_loans_count", "monthly_expense", "late_payments", "risk_flag",
        "employment_years", "defaulted_before",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- engineered features ---------------------------------------------
    # Debt-to-income ratio: monthly expenses relative to monthly gross income.
    # NOTE (assumption): the dataset has no explicit "monthly debt payment"
    # field, so monthly_expense is used as the debt-service proxy.
    df["debt_to_income_ratio"] = (df["monthly_expense"] / (df["annual_income"] / 12)).round(4)

    # Credit-score risk tiers (standard FICO-style bands)
    bins = [299, 579, 669, 739, 799, 850]
    labels = ["Poor", "Fair", "Good", "Very Good", "Exceptional"]
    df["credit_risk_tier"] = pd.cut(df["credit_score"], bins=bins, labels=labels)

    # Income groups for "avg loan size by income group" analysis
    income_bins = [0, 30000, 60000, 90000, np.inf]
    income_labels = ["<30K", "30K-60K", "60K-90K", "90K+"]
    df["income_group"] = pd.cut(df["annual_income"], bins=income_bins, labels=income_labels)

    # Convenience numeric flag for approval-rate calculations
    df["approved_flag"] = (df["approval_status"] == "Approved").astype(int)

    # Late-payment risk banding
    df["late_payment_band"] = pd.cut(
        df["late_payments"], bins=[-1, 0, 2, np.inf], labels=["0", "1-2", "3+"]
    )

    logger.info("Transformation complete. Added columns: debt_to_income_ratio, "
                "credit_risk_tier, income_group, approved_flag, late_payment_band.")
    return df


# ---------------------------------------------------------------------------
# 3. VALIDATE
# ---------------------------------------------------------------------------
def validate_credit_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforce data-quality rules for income, credit score, and age.
    Rows failing any rule are dropped; a summary is logged.
    Also drops exact duplicate applicant_id records.
    """
    logger.info("Validating data ...")
    start_n = len(df)
    issues = {}

    # Rule 1: valid income (must be positive, non-null)
    bad_income = df["annual_income"].isna() | (df["annual_income"] <= 0)
    issues["invalid_income"] = int(bad_income.sum())

    # Rule 2: valid credit score (300-850 inclusive, standard FICO range)
    bad_score = df["credit_score"].isna() | ~df["credit_score"].between(300, 850)
    issues["invalid_credit_score"] = int(bad_score.sum())

    # Rule 3: valid age (working-age adult, 18-100)
    bad_age = df["age"].isna() | ~df["age"].between(18, 100)
    issues["invalid_age"] = int(bad_age.sum())

    # Rule 4: valid loan amount (must be positive)
    bad_loan = df["loan_amount"].isna() | (df["loan_amount"] <= 0)
    issues["invalid_loan_amount"] = int(bad_loan.sum())

    # Rule 5: no duplicate applicants
    dup_mask = df.duplicated(subset="applicant_id", keep="first")
    issues["duplicate_applicant_id"] = int(dup_mask.sum())

    bad_rows = bad_income | bad_score | bad_age | bad_loan | dup_mask
    clean_df = df.loc[~bad_rows].reset_index(drop=True)

    for rule, count in issues.items():
        logger.info(f"  {rule}: {count} row(s) flagged")

    removed = start_n - len(clean_df)
    logger.info(f"Validation complete. {removed} row(s) removed, "
                f"{len(clean_df):,} row(s) passed all checks "
                f"({len(clean_df)/start_n:.2%} retained).")

    return clean_df


# ---------------------------------------------------------------------------
# 4. SAVE
# ---------------------------------------------------------------------------
def save_credit_data(df: pd.DataFrame, csv_path: Path = CLEAN_CSV_PATH,
                      db_path: Path = CLEAN_DB_PATH, table_name: str = "credit_applications") -> None:
    """
    Persist the cleaned dataset:
      - CSV  -> ready for Tableau / Power BI import
      - SQLite DB -> ready for SQL analysis (Phase 2)
    """
    logger.info(f"Saving cleaned CSV to {csv_path} ...")
    df.to_csv(csv_path, index=False)

    logger.info(f"Saving cleaned data to SQLite DB {db_path} (table: {table_name}) ...")
    # SQLite has no native category/datetime dtype handling via to_sql for category cols;
    # cast categories to plain strings and dates to ISO strings for a portable DB.
    df_sql = df.copy()
    for col in df_sql.select_dtypes(include="category").columns:
        df_sql[col] = df_sql[col].astype(str)
    df_sql["application_date"] = df_sql["application_date"].dt.strftime("%Y-%m-%d")

    with sqlite3.connect(db_path) as conn:
        df_sql.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_region ON {table_name}(region);")
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_purpose ON {table_name}(loan_purpose);")
        conn.commit()

    logger.info("Save complete.")


# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------
def run_pipeline(raw_path: Path = RAW_PATH) -> pd.DataFrame:
    raw = extract_credit_data(raw_path)
    transformed = transform_credit_data(raw)
    clean = validate_credit_data(transformed)
    save_credit_data(clean)
    return clean


if __name__ == "__main__":
    final_df = run_pipeline()
    print("\n--- Pipeline finished ---")
    print(final_df[["credit_score", "credit_risk_tier", "debt_to_income_ratio",
                     "income_group", "approved_flag"]].head(10).to_string())
