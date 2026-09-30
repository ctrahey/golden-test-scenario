"""Generate the Kestrel Sports Co. demo datasets (stdlib only, deterministic).

    python3 generator/generate.py            # writes ./data/<schema>/<table>.csv
"""
import csv
import math
import os
import random
from collections import defaultdict
from datetime import date, timedelta

import scenario as S

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "data")
rng = random.Random(S.SEED)


# --------------------------------------------------------------------------- helpers
def add_months(d, n):
    y, m = divmod(d.month - 1 + n, 12)
    return date(d.year + y, m + 1, 1)


def months(start, end):
    d = start
    while d <= end:
        yield d
        d = add_months(d, 1)


def years_since_start(d):
    return (d - S.HISTORY_START).days / 365.25


def noise(sigma):
    """Mean-one lognormal noise."""
    return math.exp(rng.gauss(0, sigma) - sigma * sigma / 2)


def seasonality(sport, d):
    m = d.month - 1 + (d.day - 1) / 30.0
    return 1 + sport["amp"] * math.cos(2 * math.pi * (m - (sport["peak"] - 1)) / 12)


RETAIL_CALENDAR = {1: 0.85, 11: 1.15, 12: 1.45}


def participation(metro, sport, d):
    """Share of the metro population actively playing the sport at date d (the latent truth)."""
    t = years_since_start(d)
    return (sport["participation"] * S.affinity(metro, sport)
            * S.trend(sport["sport_id"], metro["metro_id"], t, d)
            * math.exp(S.BOOM.get(metro["metro_id"], 0.0) * t))


def rel_interest(metro, sport, d):
    """Per-capita interest relative to the sport's 2022 national baseline (1.0 = typical)."""
    return participation(metro, sport, d) / sport["participation"]


def write(schema, table, header, rows):
    path = os.path.join(OUT, schema, f"{table}.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(["" if v is None else v for v in r])
    print(f"  {schema}.{table:<34} {len(rows):>8,} rows")


def b(v):
    return "true" if v else "false"


# --------------------------------------------------------------------------- reference
def gen_reference():
    write("ref", "dim_metro",
          ["metro_id", "metro_name", "state", "region", "population", "pop_growth_5yr_pct",
           "median_hh_income_usd", "lat", "lon", "kestrel_store_count", "has_kestrel_store",
           "first_store_open_year", "world_cup_2026_host_city"],
          [[m["metro_id"], m["metro_name"], m["state"], m["region"], int(m["population_m"] * 1e6),
            m["pop_growth_5yr_pct"], m["median_hh_income_k"] * 1000, m["lat"], m["lon"], m["store_count"],
            b(m["store_count"] > 0), m["first_store_year"], b(m["world_cup_2026_host"])] for m in S.METROS])
    write("ref", "dim_sport",
          ["sport_id", "sport_name", "department", "carried_by_kestrel", "league_data_partner"],
          [[s["sport_id"], s["sport_name"], s["department"], b(s["carried"]), s["league"]] for s in S.SPORTS])


# --------------------------------------------------------------------------- internal: sales
def gen_sales():
    """internal.sales_monthly. Returns {(month, metro_id, sport_id): (net_sales, units)} across channels."""
    rows, totals = [], defaultdict(lambda: [0.0, 0.0])
    online_by_metro = defaultdict(float)
    for m in S.METROS:
        pop = m["population_m"] * 1e6
        has_store = m["store_count"] > 0
        density = (m["store_count"] / (m["population_m"] / 1.6)) ** 0.25 if has_store else 0
        for s in S.SPORTS:
            if not s["carried"]:
                continue
            for mo in months(S.HISTORY_START, S.LAST_CLOSED_MONTH):
                mid = mo + timedelta(days=14)
                t = years_since_start(mid)
                demand = (pop * participation(m, s, mid) * s["spend"] / 12 * seasonality(s, mid)
                          * RETAIL_CALENDAR.get(mo.month, 1.0) * S.event_multiplier("sales", m, s["sport_id"], mid))
                channels = []
                if has_store:
                    share = (s["share"] * density * S.capture_modifier(m["metro_id"], s["sport_id"], t)
                             * math.exp(S.STORE_TRAFFIC_TREND.get(m["metro_id"], 0.0) * t))
                    in_stock = min(0.99, S.in_stock_rate(m["metro_id"], s["sport_id"], t) + rng.gauss(0, 0.012))
                    channels.append(("store", demand * share * noise(0.05), round(in_stock, 3)))
                online_share = (S.ONLINE_SHARE_STORE_METRO if has_store else S.ONLINE_SHARE_NO_STORE) * s["share"] / 0.07
                channels.append(("online", demand * online_share * math.exp(S.ONLINE_GROWTH * t) * noise(0.08), None))
                for channel, sales, in_stock in channels:
                    asp = s["asp"] * (1.08 if channel == "online" else 1.0) * noise(0.03)
                    units = max(1, round(sales / asp))
                    rows.append([mo.isoformat(), m["metro_id"], s["sport_id"], channel, round(sales, 2), units,
                                 max(1, round(units / (1.5 if channel == "store" else 1.8))),
                                 round(sales * s["margin"] * noise(0.03), 2), in_stock])
                    totals[(mo, m["metro_id"], s["sport_id"])][0] += sales
                    totals[(mo, m["metro_id"], s["sport_id"])][1] += units
                    if channel == "online":
                        online_by_metro[(m["metro_id"], mo)] += sales
    write("internal", "sales_monthly",
          ["month", "metro_id", "sport_id", "channel", "net_sales_usd", "units", "orders",
           "gross_margin_usd", "in_stock_rate"], rows)
    return totals, online_by_metro


# --------------------------------------------------------------------------- internal: products
def product_catalog():
    cat, i = [], 0
    for sid, items in S.PRODUCTS.items():
        for k, (item, launch, pmult) in enumerate(items):
            brand = "Kestrel Pro" if k == 2 else S.BRANDS[(i + k) % len(S.BRANDS)]
            cat.append(dict(product_id=f"P{sid}{k + 1:02d}", product_name=f"{brand} {item}", brand=brand,
                            sport_id=sid, launch=launch, price=round(S.SPORT_BY_ID[sid]["asp"] * pmult, 2),
                            weight=S.BASE_PRODUCT_WEIGHTS[k]))
        i += 1
    return cat


def product_share(products, d):
    w = []
    for p in products:
        if p["launch"] is None:
            w.append(p["weight"])
        else:
            ramp = (d - p["launch"]).days / 365.25 / 0.6   # full weight ~7 months after launch
            w.append(0.0 if ramp <= 0 else p["weight"] * 2.2 * min(1.0, ramp))
    tot = sum(w)
    return [x / tot for x in w]


def gen_products(totals):
    cat = product_catalog()
    write("internal", "dim_product",
          ["product_id", "product_name", "brand", "sport_id", "launch_date", "list_price_usd", "is_private_label"],
          [[p["product_id"], p["product_name"], p["brand"], p["sport_id"],
            p["launch"].isoformat() if p["launch"] else None, p["price"], b(p["brand"] == "Kestrel Pro")] for p in cat])

    by_sport = defaultdict(list)
    for p in cat:
        by_sport[p["sport_id"]].append(p)
    quarters = [date(y, q, 1) for y in range(2022, 2027) for q in (1, 4, 7, 10) if date(y, q, 1) <= date(2026, 4, 1)]
    q_units = {}   # (q, metro, product_id) -> units
    for m in S.METROS:
        for sid, prods in by_sport.items():
            for q in quarters:
                sport_units = sum(totals[(add_months(q, k), m["metro_id"], sid)][1] for k in range(3))
                shares = product_share(prods, q + timedelta(days=45))
                for p, sh in zip(prods, shares):
                    q_units[(q, m["metro_id"], p["product_id"])] = round(sport_units * sh * noise(0.06))
    rows = []
    for m in S.METROS:
        for q in quarters[4:]:
            prev = date(q.year - 1, q.month, 1)
            cands = []
            for p in cat:
                u, pu = q_units[(q, m["metro_id"], p["product_id"])], q_units[(prev, m["metro_id"], p["product_id"])]
                if u >= 20:
                    cands.append((u - pu, p, u, pu))
            cands.sort(key=lambda c: -c[0])
            for rank, (chg, p, u, pu) in enumerate(cands[:10], 1):
                rows.append([q.isoformat(), f"{q.year}-Q{(q.month - 1) // 3 + 1}", m["metro_id"], rank,
                             p["product_id"], p["product_name"], p["sport_id"], u, pu, chg,
                             round(100 * chg / pu, 1) if pu else None, b(pu == 0)])
    write("internal", "top_trending_products_quarterly",
          ["quarter_start", "quarter_label", "metro_id", "trend_rank", "product_id", "product_name", "sport_id",
           "units", "units_same_q_prior_year", "unit_change_yoy", "pct_change_yoy", "is_new_launch"], rows)


# --------------------------------------------------------------------------- internal: ad interest program
CREATIVE = {"RUN": "Couch to 10K in 8 weeks", "CYC": "Best local gravel loops", "SOC": "Juggling drills from the pros",
            "BSK": "Fix your jump shot", "BSB": "How to pick a bat", "FTB": "Flag football for families",
            "GLF": "Break 90 this season", "TEN": "Serve like a pro", "PKB": "5 drills to fix your dink",
            "PDL": "Padel 101: walls are your friend", "LAX": "Cradling basics for new players",
            "HKY": "Learn to skate: adult edition", "SNW": "Carve your first black run",
            "CLM": "Bouldering grades explained", "VOL": "Serve-receive fundamentals"}


def gen_ads():
    rows, d = [], S.AD_PROGRAM_START
    while d <= S.EXTERNAL_LAST_WEEK:
        mid = d + timedelta(days=3)
        for m in S.METROS:
            for s in S.SPORTS:
                imps = round(m["population_m"] * 1e6 * 0.004 * noise(0.10))
                ctr = min(0.05, 0.008 * rel_interest(m, s, mid) ** 0.6 * seasonality(s, mid) ** 0.5
                          * S.event_multiplier("ads", m, s["sport_id"], mid) * noise(0.08))
                clicks = round(imps * ctr)
                spend = imps / 1000 * 6.5 * noise(0.05)
                rows.append([d.isoformat(), m["metro_id"], s["sport_id"], f"KSC-FanContent-{s['sport_id']}",
                             CREATIVE[s["sport_id"]], imps, clicks, round(clicks / imps, 5),
                             round(clicks * 0.22 * noise(0.1)), round(spend, 2)])
        d += timedelta(days=7)
    write("internal", "ad_interest_program_weekly",
          ["week_start", "metro_id", "sport_id", "campaign_name", "creative_theme", "impressions", "clicks",
           "ctr", "engaged_views_30s", "spend_usd"], rows)


# --------------------------------------------------------------------------- external: search vendor
def gen_search():
    rows, d = [], date(2022, 1, 3)
    while d <= S.EXTERNAL_LAST_WEEK:
        lead = d + timedelta(days=90)   # search leads purchases by about a quarter
        for m in S.METROS:
            infl = S.SEARCH_INFLATION.get(m["metro_id"], 1.0)
            for s in S.SPORTS:
                base = (100 * rel_interest(m, s, lead) * seasonality(s, d) ** 1.3 * infl
                        * S.event_multiplier("search", m, s["sport_id"], d))
                for k, term in enumerate(s["terms"]):
                    idx = base * (1.0 if k == 0 else 0.55) * noise(0.12)
                    rows.append([d.isoformat(), m["metro_id"], s["sport_id"], term,
                                 "product" if k == 0 else "local_intent", round(idx, 1)])
        d += timedelta(days=7)
    write("external", "search_trends_weekly",
          ["week_start", "metro_id", "sport_id", "search_term", "term_type", "search_interest_index"], rows)


# --------------------------------------------------------------------------- external: league registrations
def gen_registrations():
    rows, prior = [], {}
    for year in range(2022, 2027):
        for season, month in (("Spring", 3), ("Fall", 9)):
            sd = date(year, month, 1)
            for s in S.SPORTS:
                if not s["league"] or season not in s["reg_seasons"]:
                    continue
                if s["sport_id"] == "PDL" and (year, month) < (S.PADEL_LEAGUE_START_YEAR, 9):
                    continue
                for m in S.METROS:
                    total = (m["population_m"] * 1e6 * participation(m, s, sd) * 0.12
                             * s["reg_seasons"][season] * noise(0.05))
                    for band, frac in (("Youth (U18)", s["youth_share"]), ("Adult (18+)", 1 - s["youth_share"])):
                        reg = max(0, round(total * frac))
                        key = (season, s["sport_id"], m["metro_id"], band)
                        retained = min(reg * 0.9, 0.72 * prior[key]) if key in prior else reg * 0.7
                        rows.append([f"{year} {season}", sd.isoformat(), m["metro_id"], s["sport_id"], s["league"],
                                     band, reg, max(0, round(reg - retained)), b((year, month) == (2026, 9))])
                        prior[key] = reg
    write("external", "league_registrations",
          ["season", "season_start_date", "metro_id", "sport_id", "league_name", "age_band", "registrations",
           "new_registrants", "is_preliminary"], rows)


# --------------------------------------------------------------------------- forecast
def gen_forecast(totals, online_by_metro):
    """FP&A baseline: internal sales history only -> damped trailing growth x last-year seasonality."""
    rows = []
    last = S.LAST_CLOSED_MONTH
    keys = {(mid, sid) for (_, mid, sid) in totals}
    for mid, sid in sorted(keys):
        hist = {mo: totals[(mo, mid, sid)][0] for mo in months(S.HISTORY_START, last)}
        ttm = sum(hist[add_months(last, -k)] for k in range(12))
        prev = sum(hist[add_months(last, -12 - k)] for k in range(12))
        g = max(-0.15, min(0.25, 0.5 * (ttm / prev - 1)))
        series = dict(hist)
        for h, mo in enumerate(months(add_months(last, 1), S.FORECAST_END_MONTH), 1):
            p50 = series[add_months(mo, -12)] * (1 + g)
            series[mo] = p50
            spread = 0.07 + 0.012 * h
            rows.append([mo.isoformat(), mid, sid, round(p50 * (1 - 1.28 * spread), 2), round(p50, 2),
                         round(p50 * (1 + 1.28 * spread), 2), round(100 * g, 1), "FP&A Baseline TS v3",
                         S.FORECAST_VERSION.isoformat()])
    write("forecast", "sales_baseline_monthly",
          ["forecast_month", "metro_id", "sport_id", "net_sales_p10_usd", "net_sales_p50_usd", "net_sales_p90_usd",
           "assumed_annual_growth_pct", "model_name", "forecast_version"], rows)

    cand = []
    for m in S.METROS:
        if m["store_count"]:
            continue
        online_ttm = sum(online_by_metro[(m["metro_id"], add_months(last, -k))] for k in range(12))
        y1 = (4.0e6 * (m["population_m"] / 2.0) ** 0.9 * (m["median_hh_income_k"] / 80) ** 0.8
              + 0.3 * online_ttm)
        cand.append((y1, m, online_ttm))
    cand.sort(key=lambda c: -c[0])
    write("forecast", "site_selection_candidates",
          ["metro_id", "model_rank", "projected_y1_store_sales_p10_usd", "projected_y1_store_sales_p50_usd",
           "projected_y1_store_sales_p90_usd", "online_sales_ttm_usd", "model_inputs", "model_name",
           "assumed_open_date", "forecast_version"],
          [[m["metro_id"], i, round(y1 * 0.75), round(y1), round(y1 * 1.25), round(ot),
            "population; median HH income; trailing-12m online sales", "Site Model v2 (demographic)",
            "2027-09-01", S.FORECAST_VERSION.isoformat()] for i, (y1, m, ot) in enumerate(cand, 1)])


def main():
    print(f"Generating {S.COMPANY} demo data -> {OUT}")
    gen_reference()
    totals, online_by_metro = gen_sales()
    gen_products(totals)
    gen_ads()
    gen_search()
    gen_registrations()
    gen_forecast(totals, online_by_metro)


if __name__ == "__main__":
    main()
