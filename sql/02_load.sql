-- COPY every CSV from S3. ${BUCKET} is substituted by aws/run_sql.py.
-- Uses the namespace default IAM role created by the CloudFormation stack.

COPY ref.dim_metro FROM 's3://${BUCKET}/data/ref/dim_metro.csv' IAM_ROLE default CSV IGNOREHEADER 1 EMPTYASNULL;
COPY ref.dim_sport FROM 's3://${BUCKET}/data/ref/dim_sport.csv' IAM_ROLE default CSV IGNOREHEADER 1 EMPTYASNULL;
COPY internal.sales_monthly FROM 's3://${BUCKET}/data/internal/sales_monthly.csv' IAM_ROLE default CSV IGNOREHEADER 1 EMPTYASNULL;
COPY internal.dim_product FROM 's3://${BUCKET}/data/internal/dim_product.csv' IAM_ROLE default CSV IGNOREHEADER 1 EMPTYASNULL;
COPY internal.top_trending_products_quarterly FROM 's3://${BUCKET}/data/internal/top_trending_products_quarterly.csv' IAM_ROLE default CSV IGNOREHEADER 1 EMPTYASNULL;
COPY internal.ad_interest_program_weekly FROM 's3://${BUCKET}/data/internal/ad_interest_program_weekly.csv' IAM_ROLE default CSV IGNOREHEADER 1 EMPTYASNULL;
COPY external.search_trends_weekly FROM 's3://${BUCKET}/data/external/search_trends_weekly.csv' IAM_ROLE default CSV IGNOREHEADER 1 EMPTYASNULL;
COPY external.league_registrations FROM 's3://${BUCKET}/data/external/league_registrations.csv' IAM_ROLE default CSV IGNOREHEADER 1 EMPTYASNULL;
COPY forecast.sales_baseline_monthly FROM 's3://${BUCKET}/data/forecast/sales_baseline_monthly.csv' IAM_ROLE default CSV IGNOREHEADER 1 EMPTYASNULL;
COPY forecast.site_selection_candidates FROM 's3://${BUCKET}/data/forecast/site_selection_candidates.csv' IAM_ROLE default CSV IGNOREHEADER 1 EMPTYASNULL;
