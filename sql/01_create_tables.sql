-- Kestrel Sports Co. demo schema. Schemas encode provenance:
--   ref      = shared reference dimensions
--   internal = Kestrel first-party actuals (POS, e-comm, merchandising, marketing)
--   external = paid third-party data
--   forecast = projections produced by the Kestrel FP&A analytics team
-- NOTE: statements are split on semicolons by aws/run_sql.py - keep semicolons out of comments and strings.

CREATE SCHEMA IF NOT EXISTS ref;
CREATE SCHEMA IF NOT EXISTS internal;
CREATE SCHEMA IF NOT EXISTS external;
CREATE SCHEMA IF NOT EXISTS forecast;

DROP TABLE IF EXISTS ref.dim_metro;
CREATE TABLE ref.dim_metro (
  metro_id                 VARCHAR(3) PRIMARY KEY,
  metro_name               VARCHAR(64),
  state                    VARCHAR(2),
  region                   VARCHAR(32),
  population               BIGINT,
  pop_growth_5yr_pct       DECIMAL(5,1),
  median_hh_income_usd     INTEGER,
  lat                      DECIMAL(8,4),
  lon                      DECIMAL(8,4),
  kestrel_store_count      SMALLINT,
  has_kestrel_store        BOOLEAN,
  first_store_open_year    SMALLINT,
  world_cup_2026_host_city BOOLEAN
) DISTSTYLE ALL;
COMMENT ON TABLE ref.dim_metro IS 'US metro areas (reference). 20 metros with Kestrel stores plus 11 candidate expansion metros served online only.';

DROP TABLE IF EXISTS ref.dim_sport;
CREATE TABLE ref.dim_sport (
  sport_id            VARCHAR(3) PRIMARY KEY,
  sport_name          VARCHAR(32),
  department          VARCHAR(32),
  carried_by_kestrel  BOOLEAN,
  league_data_partner VARCHAR(64)
) DISTSTYLE ALL;
COMMENT ON TABLE ref.dim_sport IS 'Sport categories (reference). carried_by_kestrel=false means Kestrel does not sell this sport today (Padel).';

DROP TABLE IF EXISTS internal.sales_monthly;
CREATE TABLE internal.sales_monthly (
  month            DATE,
  metro_id         VARCHAR(3),
  sport_id         VARCHAR(3),
  channel          VARCHAR(8),
  net_sales_usd    DECIMAL(14,2),
  units            INTEGER,
  orders           INTEGER,
  gross_margin_usd DECIMAL(14,2),
  in_stock_rate    DECIMAL(5,3)
) SORTKEY (month);
COMMENT ON TABLE internal.sales_monthly IS 'INTERNAL ACTUALS. Kestrel net sales by month, metro, sport and channel (store or online). Jan 2022 to Aug 2026 (last closed month). in_stock_rate is store channel only.';

DROP TABLE IF EXISTS internal.dim_product;
CREATE TABLE internal.dim_product (
  product_id       VARCHAR(8) PRIMARY KEY,
  product_name     VARCHAR(80),
  brand            VARCHAR(32),
  sport_id         VARCHAR(3),
  launch_date      DATE,
  list_price_usd   DECIMAL(10,2),
  is_private_label BOOLEAN
) DISTSTYLE ALL;
COMMENT ON TABLE internal.dim_product IS 'INTERNAL. Kestrel product catalog (sample of top SKUs per sport).';

DROP TABLE IF EXISTS internal.top_trending_products_quarterly;
CREATE TABLE internal.top_trending_products_quarterly (
  quarter_start           DATE,
  quarter_label           VARCHAR(8),
  metro_id                VARCHAR(3),
  trend_rank              SMALLINT,
  product_id              VARCHAR(8),
  product_name            VARCHAR(80),
  sport_id                VARCHAR(3),
  units                   INTEGER,
  units_same_q_prior_year INTEGER,
  unit_change_yoy         INTEGER,
  pct_change_yoy          DECIMAL(10,1),
  is_new_launch           BOOLEAN
) SORTKEY (quarter_start);
COMMENT ON TABLE internal.top_trending_products_quarterly IS 'INTERNAL ACTUALS. Merchandising report: top 10 products per metro per quarter ranked by YoY unit increase. 2023-Q1 to 2026-Q2.';

DROP TABLE IF EXISTS internal.ad_interest_program_weekly;
CREATE TABLE internal.ad_interest_program_weekly (
  week_start        DATE,
  metro_id          VARCHAR(3),
  sport_id          VARCHAR(3),
  campaign_name     VARCHAR(32),
  creative_theme    VARCHAR(64),
  impressions       INTEGER,
  clicks            INTEGER,
  ctr               DECIMAL(8,5),
  engaged_views_30s INTEGER,
  spend_usd         DECIMAL(12,2)
) SORTKEY (week_start);
COMMENT ON TABLE internal.ad_interest_program_weekly IS 'INTERNAL SIGNAL (first-party marketing). Geo-targeted sport content ads with roughly constant budget per capita. CTR is a proxy for local interest in each sport. Program began Jan 2024.';

DROP TABLE IF EXISTS external.search_trends_weekly;
CREATE TABLE external.search_trends_weekly (
  week_start            DATE,
  metro_id              VARCHAR(3),
  sport_id              VARCHAR(3),
  search_term           VARCHAR(64),
  term_type             VARCHAR(16),
  search_interest_index DECIMAL(8,1)
) SORTKEY (week_start);
COMMENT ON TABLE external.search_trends_weekly IS 'EXTERNAL PAID (Querylytics search panel). Per-capita search interest index by metro and term, 100 = 2022 national average for the sport. Jan 2022 to Sep 2026. Tends to lead purchases by about one quarter.';

DROP TABLE IF EXISTS external.league_registrations;
CREATE TABLE external.league_registrations (
  season            VARCHAR(16),
  season_start_date DATE,
  metro_id          VARCHAR(3),
  sport_id          VARCHAR(3),
  league_name       VARCHAR(64),
  age_band          VARCHAR(16),
  registrations     INTEGER,
  new_registrants   INTEGER,
  is_preliminary    BOOLEAN
) SORTKEY (season_start_date);
COMMENT ON TABLE external.league_registrations IS 'EXTERNAL PAID (partner league data share). Anonymized player registrations by season, metro, sport and age band. Spring 2022 to Fall 2026 (Fall 2026 preliminary). Padel data starts Fall 2023. Not all sports have a league partner.';

DROP TABLE IF EXISTS forecast.sales_baseline_monthly;
CREATE TABLE forecast.sales_baseline_monthly (
  forecast_month            DATE,
  metro_id                  VARCHAR(3),
  sport_id                  VARCHAR(3),
  net_sales_p10_usd         DECIMAL(14,2),
  net_sales_p50_usd         DECIMAL(14,2),
  net_sales_p90_usd         DECIMAL(14,2),
  assumed_annual_growth_pct DECIMAL(6,1),
  model_name                VARCHAR(32),
  forecast_version          DATE
) SORTKEY (forecast_month);
COMMENT ON TABLE forecast.sales_baseline_monthly IS 'PROJECTED (FP&A analytics team). Baseline net sales forecast Sep 2026 to Dec 2027, all channels. Built from internal sales history only - damped trailing growth times prior-year seasonality. Carried sports only.';

DROP TABLE IF EXISTS forecast.site_selection_candidates;
CREATE TABLE forecast.site_selection_candidates (
  metro_id                         VARCHAR(3),
  model_rank                       SMALLINT,
  projected_y1_store_sales_p10_usd BIGINT,
  projected_y1_store_sales_p50_usd BIGINT,
  projected_y1_store_sales_p90_usd BIGINT,
  online_sales_ttm_usd             BIGINT,
  model_inputs                     VARCHAR(80),
  model_name                       VARCHAR(40),
  assumed_open_date                DATE,
  forecast_version                 DATE
);
COMMENT ON TABLE forecast.site_selection_candidates IS 'PROJECTED (FP&A analytics team). Demographic site-selection model output for metros without a Kestrel store: projected first-year store sales and rank.';
