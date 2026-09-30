"""Load ./data into in-memory SQLite and print the numbers each demo beat depends on.

    python3 generator/check_story.py
"""
import csv
import glob
import os
import sqlite3

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db = sqlite3.connect(":memory:")
for path in glob.glob(os.path.join(ROOT, "data", "*", "*.csv")):
    schema, table = path.split(os.sep)[-2], os.path.basename(path)[:-4]
    with open(path) as f:
        r = csv.reader(f)
        cols = next(r)
        name = f"{schema}_{table}"
        db.execute(f"CREATE TABLE {name} ({', '.join(cols)})")
        db.executemany(f"INSERT INTO {name} VALUES ({', '.join('?' * len(cols))})",
                       ([None if v == "" else v for v in row] for row in r))


def show(title, sql):
    cur = db.execute(sql)
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    print(f"\n== {title}")
    widths = [max(len(str(c)), *(len(f"{v:,.1f}" if isinstance(v, float) else str(v)) for v in col))
              for c, col in zip(cols, zip(*rows))] if rows else [len(c) for c in cols]
    print("  " + "  ".join(c.rjust(w) for c, w in zip(cols, widths)))
    for row in rows:
        print("  " + "  ".join((f"{v:,.1f}" if isinstance(v, float) else str(v)).rjust(w) for v, w in zip(row, widths)))


YTD = "strftime('%m', month) <= '08'"

show("Beat 1: sales by sport, 2026 YTD vs 2025 YTD (Jan-Aug)", f"""
SELECT s.sport_name,
       SUM(CASE WHEN month LIKE '2026%' THEN net_sales_usd END)/1e6 AS ytd26_m,
       100.0*(SUM(CASE WHEN month LIKE '2026%' THEN net_sales_usd END)
            / SUM(CASE WHEN month LIKE '2025%' THEN net_sales_usd END) - 1) AS yoy_pct
FROM internal_sales_monthly x JOIN ref_dim_sport s USING (sport_id)
WHERE {YTD} GROUP BY 1 ORDER BY yoy_pct DESC""")

show("Beat 1/2: metro store-sales YoY vs search YoY (declining metros first)", f"""
WITH sales AS (
  SELECT metro_id, 100.0*(SUM(CASE WHEN month LIKE '2026%' THEN net_sales_usd END)
                        / SUM(CASE WHEN month LIKE '2025%' THEN net_sales_usd END) - 1) AS sales_yoy
  FROM internal_sales_monthly WHERE channel='store' AND {YTD} GROUP BY 1),
srch AS (
  SELECT metro_id, 100.0*(AVG(CASE WHEN week_start BETWEEN '2026-01-01' AND '2026-08-31' THEN search_interest_index END)
                        / AVG(CASE WHEN week_start BETWEEN '2025-01-01' AND '2025-08-31' THEN search_interest_index END) - 1) AS search_yoy
  FROM external_search_trends_weekly WHERE sport_id <> 'SOC' GROUP BY 1)
SELECT metro_id, sales_yoy, search_yoy FROM sales JOIN srch USING (metro_id) ORDER BY sales_yoy LIMIT 6""")

show("Beat 2: golf -- internal vs external both falling", """
SELECT substr(month,1,4) AS yr, SUM(net_sales_usd)/1e6 AS golf_sales_m,
  (SELECT AVG(search_interest_index) FROM external_search_trends_weekly
    WHERE sport_id='GLF' AND substr(week_start,1,4)=substr(x.month,1,4)
      AND strftime('%m', week_start) <= '08') AS golf_search_idx
FROM internal_sales_monthly x WHERE sport_id='GLF' AND strftime('%m', month) <= '08' GROUP BY 1""")

show("Beat 3: pickleball store metros -- sales growth vs registrations growth (2023 -> 2026, Spring)", """
WITH s AS (
  SELECT metro_id,
    SUM(CASE WHEN month BETWEEN '2026-01-01' AND '2026-08-01' THEN net_sales_usd END) AS s26,
    SUM(CASE WHEN month BETWEEN '2023-01-01' AND '2023-08-01' THEN net_sales_usd END) AS s23,
    AVG(CASE WHEN month >= '2026-01-01' AND channel='store' THEN in_stock_rate END) AS in_stock_26
  FROM internal_sales_monthly WHERE sport_id='PKB' GROUP BY 1),
r AS (
  SELECT metro_id, SUM(CASE WHEN season='2026 Spring' THEN registrations END) AS r26,
                   SUM(CASE WHEN season='2023 Spring' THEN registrations END) AS r23
  FROM external_league_registrations WHERE sport_id='PKB' GROUP BY 1)
SELECT metro_id, 100.0*(s26/s23-1) AS sales_growth_pct, 100.0*(1.0*r26/r23-1) AS reg_growth_pct,
       s26/r26 AS sales_per_registrant, in_stock_26
FROM s JOIN r USING (metro_id) JOIN ref_dim_metro m USING (metro_id)
WHERE m.has_kestrel_store='true' ORDER BY sales_per_registrant""")

show("Beat 4: padel whitespace -- signals by metro (we sell $0)", """
SELECT metro_id,
  SUM(CASE WHEN season='2026 Spring' THEN registrations END) AS reg_spring26,
  SUM(CASE WHEN season='2024 Spring' THEN registrations END) AS reg_spring24,
  (SELECT 100*AVG(ctr) FROM internal_ad_interest_program_weekly a
     WHERE a.sport_id='PDL' AND a.metro_id=r.metro_id AND week_start >= '2026-06-01') AS ctr_pct_recent,
  (SELECT COALESCE(SUM(net_sales_usd),0) FROM internal_sales_monthly x WHERE x.sport_id='PDL' AND x.metro_id=r.metro_id) AS kestrel_sales
FROM external_league_registrations r WHERE sport_id='PDL' GROUP BY 1 ORDER BY reg_spring26 DESC LIMIT 8""")

show("Beat 5: candidate metros -- FP&A site model vs outside-in growth signals", """
WITH srch AS (
  SELECT metro_id, 100.0*(AVG(CASE WHEN week_start BETWEEN '2026-01-01' AND '2026-08-31' THEN search_interest_index END)
                        / AVG(CASE WHEN week_start BETWEEN '2024-01-01' AND '2024-08-31' THEN search_interest_index END) - 1) AS search_g
  FROM external_search_trends_weekly WHERE sport_id <> 'SOC' GROUP BY 1),
reg AS (
  SELECT metro_id, 100.0*(1.0*SUM(CASE WHEN season='2026 Spring' THEN registrations END)
                        / SUM(CASE WHEN season='2024 Spring' THEN registrations END) - 1) AS reg_g,
         1e5*SUM(CASE WHEN season='2026 Spring' THEN registrations END) / MAX(m.population) AS reg_per_100k
  FROM external_league_registrations JOIN ref_dim_metro m USING (metro_id) WHERE sport_id <> 'PDL' GROUP BY 1),
ads AS (
  SELECT metro_id, 100*AVG(CASE WHEN week_start >= '2026-01-01' THEN ctr END) AS ctr_26,
         100.0*(AVG(CASE WHEN week_start >= '2026-01-01' THEN ctr END)
              / AVG(CASE WHEN week_start < '2024-09-01' THEN ctr END) - 1) AS ctr_g
  FROM internal_ad_interest_program_weekly GROUP BY 1),
onl AS (
  SELECT metro_id, 100.0*(SUM(CASE WHEN month LIKE '2026%' THEN net_sales_usd END)
                        / SUM(CASE WHEN month LIKE '2024%' AND strftime('%m', month) <= '08' THEN net_sales_usd END) - 1) AS online_g
  FROM internal_sales_monthly WHERE channel='online' AND strftime('%m', month) <= '08' GROUP BY 1)
SELECT c.metro_id, c.model_rank, c.projected_y1_store_sales_p50_usd/1e6 AS y1_m,
       search_g, reg_g, reg_per_100k, ctr_26, ctr_g, online_g
FROM forecast_site_selection_candidates c JOIN srch USING (metro_id) JOIN reg USING (metro_id)
JOIN ads USING (metro_id) JOIN onl USING (metro_id) ORDER BY reg_g DESC""")

show("Anomaly: soccer search, WC host vs non-host (Jun-Jul 2026 vs Jun-Jul 2025)", """
SELECT m.world_cup_2026_host_city AS host,
  AVG(CASE WHEN week_start BETWEEN '2026-06-15' AND '2026-07-19' THEN search_interest_index END) /
  AVG(CASE WHEN week_start BETWEEN '2025-06-15' AND '2025-07-19' THEN search_interest_index END) AS ratio
FROM external_search_trends_weekly JOIN ref_dim_metro m USING (metro_id) WHERE sport_id='SOC' GROUP BY 1""")

show("Trap: Las Vegas search level vs registrations per capita (2026)", """
SELECT m.metro_id,
  (SELECT AVG(search_interest_index) FROM external_search_trends_weekly s
     WHERE s.metro_id=m.metro_id AND week_start >= '2026-01-01' AND sport_id <> 'SOC') AS search_idx_26,
  (SELECT 1e5*SUM(registrations)/m.population FROM external_league_registrations r
     WHERE r.metro_id=m.metro_id AND season='2026 Spring') AS reg_per_100k
FROM ref_dim_metro m WHERE m.has_kestrel_store='false' ORDER BY search_idx_26 DESC""")
