"""Story knobs for the Kestrel Sports Co. demo. See docs/STORY.md.

Everything that shapes the narrative lives here; generate.py is mechanics only.
"""
import math
from datetime import date

COMPANY = "Kestrel Sports Co."
SEED = 20260928

HISTORY_START = date(2022, 1, 1)
LAST_CLOSED_MONTH = date(2026, 8, 1)      # internal actuals end here
EXTERNAL_LAST_WEEK = date(2026, 9, 21)    # vendor feeds run ~3 weeks ahead of the close
AD_PROGRAM_START = date(2024, 1, 1)
PADEL_LEAGUE_START_YEAR = 2023            # padel league data share begins Fall 2023
FORECAST_VERSION = date(2026, 9, 15)
FORECAST_END_MONTH = date(2027, 12, 1)

# --------------------------------------------------------------------------- metros
# id, name, state, region, pop (M), 5yr pop growth %, median HH income ($k), lat, lon,
# store_count, first_store_year, 2026 World Cup host
_METROS = [
    # Store metros
    ("NYC", "New York",          "NY", "Northeast",     19.5,  0.8,  98, 40.71,  -74.01, 6, 2009, True),
    ("LAX", "Los Angeles",       "CA", "Pacific",       12.8, -0.5,  90, 34.05, -118.24, 5, 2010, True),
    ("CHI", "Chicago",           "IL", "Midwest",        9.3, -0.3,  85, 41.88,  -87.63, 4, 2011, False),
    ("DFW", "Dallas-Fort Worth", "TX", "South Central",  8.1,  9.5,  87, 32.78,  -96.80, 4, 2012, True),
    ("HOU", "Houston",           "TX", "South Central",  7.5,  8.0,  80, 29.76,  -95.37, 3, 2013, True),
    ("WAS", "Washington DC",     "DC", "Northeast",      6.3,  3.5, 118, 38.91,  -77.04, 3, 2012, False),
    ("PHL", "Philadelphia",      "PA", "Northeast",      6.2,  1.0,  88, 39.95,  -75.17, 2, 2014, True),
    ("ATL", "Atlanta",           "GA", "Southeast",      6.3,  8.0,  86, 33.75,  -84.39, 3, 2013, True),
    ("MIA", "Miami",             "FL", "Southeast",      6.2,  4.5,  73, 25.76,  -80.19, 3, 2015, True),
    ("PHX", "Phoenix",           "AZ", "Southwest",      5.1,  9.0,  82, 33.45, -112.07, 3, 2014, False),
    ("BOS", "Boston",            "MA", "Northeast",      4.9,  1.5, 110, 42.36,  -71.06, 2, 2012, True),
    ("SFO", "San Francisco",     "CA", "Pacific",        4.6, -2.5, 130, 37.77, -122.42, 2, 2011, True),
    ("SEA", "Seattle",           "WA", "Pacific",        4.0,  5.0, 110, 47.61, -122.33, 2, 2013, True),
    ("MSP", "Minneapolis",       "MN", "Midwest",        3.7,  3.0,  95, 44.98,  -93.27, 2, 2014, False),
    ("SAN", "San Diego",         "CA", "Pacific",        3.3,  1.5,  98, 32.72, -117.16, 2, 2016, False),
    ("TPA", "Tampa",             "FL", "Southeast",      3.3,  9.5,  71, 27.95,  -82.46, 2, 2016, False),
    ("DEN", "Denver",            "CO", "Mountain",       3.0,  6.5,  98, 39.74, -104.99, 2, 2015, False),
    ("ORL", "Orlando",           "FL", "Southeast",      2.8, 10.0,  72, 28.54,  -81.38, 2, 2017, False),
    ("POR", "Portland",          "OR", "Pacific",        2.5,  3.0,  90, 45.52, -122.68, 1, 2018, False),
    ("DET", "Detroit",           "MI", "Midwest",        4.3, -0.5,  72, 42.33,  -83.05, 2, 2015, False),
    # Candidate metros (no stores; online sales only)
    ("NSH", "Nashville",         "TN", "Southeast",      2.1, 12.0,  80, 36.16,  -86.78, 0, None, False),
    ("AUS", "Austin",            "TX", "South Central",  2.5, 16.0,  95, 30.27,  -97.74, 0, None, False),
    ("RDU", "Raleigh-Durham",    "NC", "Southeast",      1.5, 13.0,  92, 35.78,  -78.64, 0, None, False),
    ("CLT", "Charlotte",         "NC", "Southeast",      2.8, 10.5,  80, 35.23,  -80.84, 0, None, False),
    ("SAT", "San Antonio",       "TX", "South Central",  2.7,  9.0,  70, 29.42,  -98.49, 0, None, False),
    ("LAS", "Las Vegas",         "NV", "Southwest",      2.3,  8.0,  70, 36.17, -115.14, 0, None, False),
    ("CMH", "Columbus",          "OH", "Midwest",        2.2,  5.5,  76, 39.96,  -83.00, 0, None, False),
    ("MCI", "Kansas City",       "MO", "Midwest",        2.2,  4.5,  78, 39.10,  -94.58, 0, None, True),
    ("SLC", "Salt Lake City",    "UT", "Mountain",       1.3,  8.0,  90, 40.76, -111.89, 0, None, False),
    ("JAX", "Jacksonville",      "FL", "Southeast",      1.7, 11.0,  75, 30.33,  -81.66, 0, None, False),
    ("BOI", "Boise",             "ID", "Mountain",       0.8, 14.0,  78, 43.62, -116.20, 0, None, False),
]
_METRO_FIELDS = ["metro_id", "metro_name", "state", "region", "population_m", "pop_growth_5yr_pct",
                 "median_hh_income_k", "lat", "lon", "store_count", "first_store_year", "world_cup_2026_host"]
METROS = [dict(zip(_METRO_FIELDS, row)) for row in _METROS]

# Extra annual growth in sports participation (log-rate), applied to every sport in the metro.
# THEME 2: Nashville / Austin / Raleigh are the hot growers; Charlotte is big but lukewarm.
BOOM = {"NSH": 0.10, "AUS": 0.08, "RDU": 0.085, "CLT": 0.015, "SAT": 0.005, "LAS": 0.0,
        "CMH": 0.01, "MCI": 0.0, "SLC": 0.03, "JAX": 0.02, "BOI": 0.035,
        "DFW": 0.02, "PHX": 0.02, "TPA": 0.02, "ORL": 0.02, "ATL": 0.015, "HOU": 0.01,
        "DEN": 0.015, "SEA": 0.01, "CHI": -0.01, "DET": -0.01}

# Store-traffic drag that hits Kestrel's store sales but NOT underlying demand ("it's us").
STORE_TRAFFIC_TREND = {"SFO": -0.075, "DET": -0.02}

# Las Vegas search is inflated by tourists; registrations and ad CTR are not ("the trap").
SEARCH_INFLATION = {"LAS": 1.9, "ORL": 1.2}

# THEME 1: Sun Belt store metros where pickleball demand outran our assortment & inventory.
PICKLE_HOT = {"PHX", "TPA", "ORL", "DFW", "HOU", "ATL", "MIA", "AUS", "NSH", "JAX", "LAS", "SAT", "RDU", "CLT"}
PICKLE_CAPTURE_GAP = {"PHX", "TPA", "ORL", "DFW", "HOU", "ATL"}

ONLINE_SHARE_STORE_METRO = 0.018   # e-comm share of market where we also have stores
ONLINE_SHARE_NO_STORE = 0.013      # e-comm share of market where we don't
ONLINE_GROWTH = 0.06               # annual e-comm channel growth

# --------------------------------------------------------------------------- sports
# participation = share of population actively playing (at 2022 national level; padel at maturity)
# spend = annual $/participant; share = Kestrel store-metro market share; peak/amp = seasonality
SPORTS = [
    dict(sport_id="RUN", sport_name="Running", department="Fitness & Outdoor", carried=True,
         participation=0.16, spend=140, share=0.075, margin=0.38, asp=62, peak=4, amp=0.15,
         youth_share=None, league=None, reg_seasons={},
         terms=["running shoes", "marathon training plan"]),
    dict(sport_id="CYC", sport_name="Cycling", department="Fitness & Outdoor", carried=True,
         participation=0.08, spend=260, share=0.05, margin=0.30, asp=85, peak=5, amp=0.35,
         youth_share=None, league=None, reg_seasons={},
         terms=["road bike", "bike repair near me"]),
    dict(sport_id="SOC", sport_name="Soccer", department="Team Sports", carried=True,
         participation=0.05, spend=170, share=0.09, margin=0.40, asp=38, peak=8, amp=0.25,
         youth_share=0.75, league="National Youth & Adult Soccer Alliance", reg_seasons={"Spring": 0.45, "Fall": 0.55},
         terms=["soccer cleats", "soccer league near me"]),
    dict(sport_id="BSK", sport_name="Basketball", department="Team Sports", carried=True,
         participation=0.07, spend=110, share=0.08, margin=0.39, asp=45, peak=11, amp=0.20,
         youth_share=0.60, league="Hoops America Rec Network", reg_seasons={"Spring": 0.25, "Fall": 0.75},
         terms=["basketball shoes", "basketball hoop"]),
    dict(sport_id="BSB", sport_name="Baseball & Softball", department="Team Sports", carried=True,
         participation=0.04, spend=220, share=0.08, margin=0.37, asp=70, peak=3, amp=0.45,
         youth_share=0.70, league="Diamond Youth Baseball Federation", reg_seasons={"Spring": 0.85, "Fall": 0.15},
         terms=["baseball bat", "softball glove"]),
    dict(sport_id="FTB", sport_name="Football", department="Team Sports", carried=True,
         participation=0.02, spend=180, share=0.08, margin=0.36, asp=55, peak=8, amp=0.55,
         youth_share=0.80, league="Gridiron Youth League Association", reg_seasons={"Spring": 0.10, "Fall": 0.90},
         terms=["football cleats", "flag football league"]),
    dict(sport_id="GLF", sport_name="Golf", department="Golf", carried=True,
         participation=0.08, spend=420, share=0.035, margin=0.28, asp=95, peak=5, amp=0.35,
         youth_share=None, league=None, reg_seasons={},
         terms=["golf clubs", "golf lessons"]),
    dict(sport_id="TEN", sport_name="Tennis", department="Racquet Sports", carried=True,
         participation=0.04, spend=160, share=0.07, margin=0.36, asp=48, peak=5, amp=0.25,
         youth_share=0.30, league="Community Tennis League of America", reg_seasons={"Spring": 0.55, "Fall": 0.45},
         terms=["tennis racquet", "tennis lessons"]),
    dict(sport_id="PKB", sport_name="Pickleball", department="Racquet Sports", carried=True,
         participation=0.02, spend=150, share=0.075, margin=0.42, asp=40, peak=4, amp=0.15,
         youth_share=0.05, league="American Pickleball League Network", reg_seasons={"Spring": 0.55, "Fall": 0.45},
         terms=["pickleball paddle", "pickleball courts near me"]),
    dict(sport_id="PDL", sport_name="Padel", department="Racquet Sports", carried=False,
         participation=0.006, spend=200, share=0.0, margin=0.40, asp=60, peak=5, amp=0.10,
         youth_share=0.05, league="US Padel Circuit", reg_seasons={"Spring": 0.5, "Fall": 0.5},
         terms=["padel racket", "padel court near me"]),
    dict(sport_id="LAX", sport_name="Lacrosse", department="Team Sports", carried=True,
         participation=0.008, spend=300, share=0.08, margin=0.38, asp=75, peak=2, amp=0.45,
         youth_share=0.70, league="US Lacrosse Club Network", reg_seasons={"Spring": 0.80, "Fall": 0.20},
         terms=["lacrosse stick", "youth lacrosse near me"]),
    dict(sport_id="HKY", sport_name="Ice Hockey", department="Team Sports", carried=True,
         participation=0.008, spend=550, share=0.06, margin=0.33, asp=110, peak=10, amp=0.45,
         youth_share=0.60, league="Amateur Hockey Federation", reg_seasons={"Spring": 0.15, "Fall": 0.85},
         terms=["hockey skates", "learn to skate hockey"]),
    dict(sport_id="SNW", sport_name="Ski & Snowboard", department="Fitness & Outdoor", carried=True,
         participation=0.035, spend=480, share=0.05, margin=0.31, asp=120, peak=12, amp=0.85,
         youth_share=None, league=None, reg_seasons={},
         terms=["ski jacket", "snowboard"]),
    dict(sport_id="CLM", sport_name="Climbing", department="Fitness & Outdoor", carried=True,
         participation=0.02, spend=180, share=0.04, margin=0.40, asp=50, peak=1, amp=0.15,
         youth_share=None, league=None, reg_seasons={},
         terms=["climbing shoes", "climbing gym near me"]),
    dict(sport_id="VOL", sport_name="Volleyball", department="Team Sports", carried=True,
         participation=0.03, spend=90, share=0.07, margin=0.40, asp=35, peak=8, amp=0.30,
         youth_share=0.55, league="National Volleyball Clubs Association", reg_seasons={"Spring": 0.30, "Fall": 0.70},
         terms=["volleyball shoes", "volleyball club near me"]),
]
SPORT_BY_ID = {s["sport_id"]: s for s in SPORTS}

# Regional affinity (multiplier on participation). Metro overrides replace the regional value.
REGION_AFFINITY = {
    "SNW": {"Mountain": 3.0, "Pacific": 1.4, "Northeast": 1.3, "Midwest": 0.9, "Southeast": 0.25,
            "South Central": 0.3, "Southwest": 0.5},
    "HKY": {"Midwest": 1.9, "Northeast": 1.8, "Mountain": 1.2, "Pacific": 0.8, "Southeast": 0.4,
            "South Central": 0.5, "Southwest": 0.5},
    "GLF": {"Southeast": 1.3, "Southwest": 1.4, "South Central": 1.2},
    "PKB": {"Southeast": 1.5, "Southwest": 1.8, "South Central": 1.4, "Mountain": 1.1},
    "PDL": {r: 0.25 for r in ["Northeast", "Pacific", "Midwest", "Southeast", "South Central", "Southwest", "Mountain"]},
    "CLM": {"Mountain": 2.3, "Pacific": 1.6},
    "LAX": {"Northeast": 1.8, "Mountain": 1.3, "Southeast": 1.0, "Midwest": 0.8, "South Central": 0.6,
            "Southwest": 0.5, "Pacific": 0.6},
    "FTB": {"Southeast": 1.4, "South Central": 1.5},
    "BSB": {"Southeast": 1.3, "South Central": 1.3, "Southwest": 1.2},
    "VOL": {"Midwest": 1.2, "South Central": 1.2, "Pacific": 1.1},
}
METRO_AFFINITY = {
    "PDL": {"MIA": 3.6, "AUS": 3.0, "NYC": 1.9, "LAX": 1.6, "DFW": 1.3, "HOU": 1.1, "NSH": 1.0, "SAN": 0.9},
    "PKB": {"PHX": 1.8, "TPA": 1.7, "ORL": 1.6, "NSH": 1.5, "AUS": 1.5},
    "SNW": {"MSP": 1.6, "SLC": 3.5, "DEN": 3.2, "BOI": 2.6, "SEA": 1.8, "POR": 1.7},
    "HKY": {"MSP": 3.2, "DET": 2.5, "BOS": 2.3},
    "LAX": {"WAS": 2.6, "BOS": 2.2, "DEN": 1.6, "NSH": 1.6, "RDU": 2.0, "CLT": 1.4, "ATL": 1.3},
    "CLM": {"DEN": 2.6, "SLC": 2.8, "BOI": 2.0},
}


def affinity(metro, sport):
    sid, mid = sport["sport_id"], metro["metro_id"]
    if mid in METRO_AFFINITY.get(sid, {}):
        return METRO_AFFINITY[sid][mid]
    return REGION_AFFINITY.get(sid, {}).get(metro["region"], 1.0)


# --------------------------------------------------------------------------- trends
def trend(sport_id, metro_id, t, d):
    """Multiplier on 2022 participation. t = years since 2022-01-01, d = date."""
    if sport_id == "PKB":   # sustained boom (~3x since 2022 in hot metros); hottest in the Sun Belt
        a = 0.50 if metro_id in PICKLE_HOT else 0.32
        return 1 + a * t
    if sport_id == "PDL":   # logistic take-off centred ~spring 2025
        return 0.04 + 1.0 / (1 + math.exp(-1.7 * (t - 3.2)))
    if sport_id == "TEN":   # pickleball cannibalises tennis where pickleball is hot
        return math.exp((-0.045 if metro_id in PICKLE_HOT else -0.015) * t)
    if sport_id == "CYC":   # post-pandemic bike bust, then flat
        return math.exp(-0.09 * min(t, 2.5))
    if sport_id == "SNW":   # bad snow winter 2023-24
        bad = date(2023, 11, 1) <= d <= date(2024, 3, 31)
        return 0.72 if bad else 1.0
    growth = {"RUN": 0.01, "SOC": 0.04, "BSK": 0.015, "BSB": 0.0, "FTB": -0.02, "GLF": -0.065,
              "LAX": 0.05, "HKY": 0.01, "CLM": 0.06, "VOL": 0.08}
    return math.exp(growth.get(sport_id, 0.0) * t)


WORLD_CUP = (date(2026, 6, 11), date(2026, 7, 19))


def event_multiplier(signal, metro, sport_id, d):
    """One-off events. signal in {'sales', 'search', 'ads'}."""
    if sport_id != "SOC":
        return 1.0
    host = metro["world_cup_2026_host"]
    if WORLD_CUP[0] <= d <= WORLD_CUP[1]:
        return {"sales": 1.15 if host else 1.05, "search": 1.8 if host else 1.3, "ads": 1.35 if host else 1.12}[signal]
    if WORLD_CUP[1] < d <= date(2026, 9, 30):
        return {"sales": 1.05 if host else 1.0, "search": 1.15 if host else 1.05, "ads": 1.1 if host else 1.0}[signal]
    return 1.0


def capture_modifier(metro_id, sport_id, t):
    """Kestrel's capture of local demand relative to its normal share (store channel)."""
    if sport_id == "PKB" and metro_id in PICKLE_CAPTURE_GAP:
        return max(0.40, 0.88 - 0.10 * t)
    return 1.0


def in_stock_rate(metro_id, sport_id, t):
    if sport_id == "PKB" and metro_id in PICKLE_CAPTURE_GAP:
        return max(0.68, 0.94 - 0.05 * t)
    return 0.955


# --------------------------------------------------------------------------- products
BRANDS = ["Kestrel Pro", "Aerion", "Stridewell", "Loftline", "Courtcraft", "Ironpeak", "Vela", "Bramble"]
# sport_id -> [(item, launch_date or None, price multiplier vs sport ASP)]
PRODUCTS = {
    "RUN": [("Tempo Road Shoe", None, 2.0), ("Trail Runner GTX", None, 2.3), ("Carbon Race Flat", date(2024, 4, 1), 3.4), ("Hydration Vest", None, 1.2)],
    "CYC": [("Gravel Bike 105", None, 14.0), ("Road Helmet MIPS", None, 1.6), ("Smart Trainer", None, 7.0), ("Bib Short", None, 1.1)],
    "SOC": [("Match Ball Pro", None, 1.0), ("FG Cleat Elite", None, 3.2), ("Shin Guard Lite", None, 0.5), ("2026 Host City Replica Ball", date(2025, 11, 1), 1.1)],
    "BSK": [("Indoor Game Ball", None, 1.4), ("Court Shoe Low", None, 2.8), ("Portable Hoop 54in", None, 8.0), ("Compression Sleeve", None, 0.4)],
    "BSB": [("BBCOR Alloy Bat", None, 2.6), ("Fielding Glove 11.75", None, 1.8), ("Batting Helmet", None, 0.9), ("USSSA Composite Bat", date(2023, 9, 1), 4.0)],
    "FTB": [("Youth Helmet", None, 3.0), ("Receiver Gloves", None, 0.8), ("Official Game Ball", None, 1.6), ("Flag Football Set", date(2024, 7, 1), 0.7)],
    "GLF": [("Game-Improvement Irons", None, 7.0), ("Distance Ball 12pk", None, 0.4), ("Stand Bag", None, 2.2), ("Launch Monitor Mini", date(2023, 6, 1), 5.5)],
    "TEN": [("Tour Racquet 98", None, 4.5), ("Pressurized Balls 3pk", None, 0.12), ("All-Court Shoe", None, 2.6), ("String Reel", None, 3.0)],
    "PKB": [("Carbon Paddle 16mm", None, 3.5), ("Outdoor Balls 6pk", None, 0.4), ("Court Shoe", None, 2.8), ("Thermoformed Pro Paddle", date(2024, 2, 1), 5.0)],
    "LAX": [("Attack Complete Stick", None, 1.4), ("Lacrosse Helmet", None, 3.0), ("Arm Guards", None, 1.0), ("Mesh Head Pro", date(2024, 9, 1), 1.6)],
    "HKY": [("Composite Stick", None, 1.9), ("Senior Skate", None, 4.0), ("Helmet Combo", None, 1.4), ("Inline Street Skate", None, 1.6)],
    "SNW": [("All-Mountain Ski", None, 5.0), ("Snowboard Boot", None, 2.4), ("Insulated Shell", None, 2.8), ("Ski Helmet MIPS", None, 1.4)],
    "CLM": [("Bouldering Shoe", None, 2.6), ("Chalk Bag", None, 0.5), ("Crash Pad", None, 4.5), ("Harness Lite", date(2024, 3, 1), 1.4)],
    "VOL": [("Indoor Game Ball", None, 1.8), ("Knee Pads", None, 0.8), ("Beach Ball Pro", None, 1.6), ("Court Shoe Mid", date(2024, 8, 1), 3.6)],
}
BASE_PRODUCT_WEIGHTS = [0.40, 0.30, 0.20, 0.10]
