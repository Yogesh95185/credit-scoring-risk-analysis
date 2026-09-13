-- =====================================================================
-- Project 2: Credit Scoring & Risk Analysis in Lending
-- Phase 2 — SQL Analysis
-- Table: credit_applications  (loaded from cleaned_credit_data.csv)
-- =====================================================================

-- 1. Top loan purposes requested
SELECT
    loan_purpose,
    COUNT(*) AS num_applications,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM credit_applications), 2) AS pct_of_total
FROM credit_applications
GROUP BY loan_purpose
ORDER BY num_applications DESC;


-- 2. Approval rates by region and by employment type
-- 2a. By region
SELECT
    region,
    COUNT(*) AS total_applications,
    SUM(CASE WHEN approval_status = 'Approved' THEN 1 ELSE 0 END) AS approved_count,
    ROUND(100.0 * SUM(CASE WHEN approval_status = 'Approved' THEN 1 ELSE 0 END) / COUNT(*), 2) AS approval_rate_pct
FROM credit_applications
GROUP BY region
ORDER BY approval_rate_pct DESC;

-- 2b. By employment type
SELECT
    employment_status,
    COUNT(*) AS total_applications,
    SUM(CASE WHEN approval_status = 'Approved' THEN 1 ELSE 0 END) AS approved_count,
    ROUND(100.0 * SUM(CASE WHEN approval_status = 'Approved' THEN 1 ELSE 0 END) / COUNT(*), 2) AS approval_rate_pct
FROM credit_applications
GROUP BY employment_status
ORDER BY approval_rate_pct DESC;


-- 3. Credit score trends vs. default history
SELECT
    defaulted_before,
    COUNT(*) AS num_applicants,
    ROUND(AVG(credit_score), 1) AS avg_credit_score,
    MIN(credit_score) AS min_credit_score,
    MAX(credit_score) AS max_credit_score
FROM credit_applications
GROUP BY defaulted_before;

-- 3b. Average credit score by risk tier x default history (finer view)
SELECT
    credit_risk_tier,
    defaulted_before,
    COUNT(*) AS num_applicants,
    ROUND(AVG(credit_score), 1) AS avg_credit_score
FROM credit_applications
GROUP BY credit_risk_tier, defaulted_before
ORDER BY
    CASE credit_risk_tier
        WHEN 'Poor' THEN 1 WHEN 'Fair' THEN 2 WHEN 'Good' THEN 3
        WHEN 'Very Good' THEN 4 WHEN 'Exceptional' THEN 5 END,
    defaulted_before;


-- 4. Risk classification by late payments
SELECT
    late_payment_band,
    COUNT(*) AS num_applicants,
    SUM(risk_flag) AS flagged_high_risk,
    ROUND(100.0 * SUM(risk_flag) / COUNT(*), 2) AS pct_flagged_high_risk,
    ROUND(100.0 * SUM(defaulted_before) / COUNT(*), 2) AS pct_defaulted_before
FROM credit_applications
GROUP BY late_payment_band
ORDER BY late_payment_band;


-- 5. Average loan size by income group
SELECT
    income_group,
    COUNT(*) AS num_applicants,
    ROUND(AVG(loan_amount), 2) AS avg_loan_amount,
    ROUND(AVG(annual_income), 2) AS avg_income,
    ROUND(AVG(debt_to_income_ratio), 3) AS avg_dti_ratio
FROM credit_applications
GROUP BY income_group
ORDER BY
    CASE income_group
        WHEN '<30K' THEN 1 WHEN '30K-60K' THEN 2
        WHEN '60K-90K' THEN 3 WHEN '90K+' THEN 4 END;
