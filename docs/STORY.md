# The Story: Kestrel Sports Co. — "Where do we grow next?"

*Everything here is invented: the company, brands, leagues and data vendors. The metros are real US metros, and populations and incomes are only roughly right.*

## The client

**Kestrel Sports Co.** is a fictional US sporting-goods retailer with **55 stores in 20 metros** and a national e-commerce site.
It's September 2026. The FY27 planning cycle is starting, and the Strategy team has two questions for leadership:

1. **Categories:** Which sports are we under-serving, and which new sport should we launch?
2. **Geos:** Where should we open our next stores?

The FP&A analytics team already has a baseline forecast and a site-selection model. **Both use only internal data plus demographics.**
The demo shows what happens when you add three outside-in demand signals.

## The two themes (keep it to these)

### Theme 1: "Racquet sports are exploding and we're leaving money on the table"
- **Pickleball.** Chain-wide sales are growing nicely, so it looks like a win. But in six Sun Belt store metros (Phoenix, Tampa, Orlando, Dallas, Houston, Atlanta), league registrations, search and ad engagement grew **much** faster than our sales. In-stock rates for pickleball in those stores fell from about 93% to the low 70s. **We're under-capturing because we can't keep paddles on the shelf.**
- **Padel** is the kicker. We don't carry it, so internal data shows **nothing**. External signals are going vertical in **Miami, Austin, New York, LA and Dallas**. The internal forecast can't see it by construction.

### Theme 2: "Our site model says Charlotte. The demand signals say Nashville."
- The FP&A site-selection model (population, income and online sales) ranks **Austin, Charlotte and San Antonio** as the top candidate metros.
- Outside-in signals (search growth, league-registration growth, ad click-through) rank **Nashville, Austin and Raleigh** first. Our own **online sales growth** in those metros was a hint hiding in plain sight.
- **Austin connects both themes.** It's #1 or #2 on every list and a padel and pickleball hotspot. So the recommendation is to open Austin as a racquet-forward format.
- **Trap metros** show why no single signal is enough:
  - **Las Vegas** has huge search volume, but it's tourists. Registrations and click-through are flat.
  - **Charlotte** is big, but it's a lukewarm grower.

### Supporting "good and bad trends" (for the opening beat)
| Trend | What internal data shows | What external data shows | Takeaway |
|---|---|---|---|
| Golf declining | Sales down about 4–5%/yr | Search and registrations also down | **The market is shrinking**, not us |
| San Francisco declining | Store sales down about 5% YoY | Signals flat | **It's us** (store traffic), not demand |
| Cycling post-pandemic bust | Down sharply 2022–24, then flat | Same | The market is normalizing |
| Volleyball, climbing, lacrosse | Growing | Growing | Healthy tailwinds |
| Soccer: 2026 World Cup | Small bump in Jun–Jul 2026 | Big search spike in host cities | A fun anomaly for auto-profiling to find |
| Snow sports, winter 2023–24 | Dip | Dip | A bad snow year |

## Data landscape (internal vs external, actual vs projected)

| Schema | Table | Owner / source | Nature | Grain | Coverage |
|---|---|---|---|---|---|
| `ref` | `dim_metro`, `dim_sport` | Strategy team | Reference | — | 31 metros, 15 sports |
| `internal` | `sales_monthly` | Kestrel POS + e-comm | **Actuals** | month × metro × sport × channel | Jan 2022 – Aug 2026 |
| `internal` | `dim_product`, `top_trending_products_quarterly` | Merchandising | **Actuals** | quarter × metro × rank | 2023-Q1 – 2026-Q2 |
| `internal` | `ad_interest_program_weekly` | Kestrel Marketing (first-party signal) | **Actuals (signal)** | week × metro × sport | Jan 2024 – Sep 2026 |
| `external` | `search_trends_weekly` | *Querylytics* (paid vendor) | **External, paid** | week × metro × search term | Jan 2022 – Sep 2026 |
| `external` | `league_registrations` | *Partner leagues* (paid data share) | **External, paid** | season × metro × sport × age band | Spring 2022 – Fall 2026 (preliminary) |
| `forecast` | `sales_baseline_monthly` | FP&A analytics team | **Projected** | month × metro × sport | Sep 2026 – Dec 2027 |
| `forecast` | `site_selection_candidates` | FP&A analytics team | **Projected** | candidate metro | FY27 site-model run |

Realistic wrinkles, which are deliberate:
- The data sources cover different time ranges. The ad program only started in 2024, and external data runs about 3 weeks past the last closed internal month.
- **Search leads sales by about a quarter.** Registrations are seasonal: some sports register only in the spring or only in the fall.
- Padel has no sales rows and no forecast rows at all. Its absence is the point.
- The Fall 2026 registrations are flagged `is_preliminary`.

## Demo walkthrough (about 20 minutes)

**Beat 0: Connect and let Golden profile.** Connect the Redshift workgroup, or upload `data/**/*.csv`. Let the automatic profiling run and see what it surfaces unprompted. With luck, the World Cup spike, the padel ramp and the golf decline.

**Beat 1: How's the business? (internal only)**
- *"Show net sales by sport, year over year, for 2026 YTD vs 2025 YTD."* Golf and cycling are down. Pickleball, volleyball and climbing are up.
- *"Which metros are declining?"* San Francisco stands out.

**Beat 2: Is it the market or is it us? (join internal to external)**
- *"For golf, compare our sales trend with the search trend and league registrations."* It's the market.
- *"Do the same for San Francisco across all sports."* Demand is flat, so it's us.

**Beat 3: Theme 1, the pickleball under-capture**
- *"Pickleball sales growth vs registration growth by store metro, 2023 to 2026."* Phoenix, Tampa and the other gap metros fall well below the trend line. Use a scatter plot.
- *"Sales per registered player, by metro."* Then drill into `in_stock_rate` to find the cause.
- *"How much revenue would we gain if the gap metros captured at the chain median?"* This sizes the prize.

**Beat 4: Theme 1 kicker, padel whitespace**
- *"Which sports have rising external signals but zero Kestrel sales?"* Padel.
- *"Padel registrations, search and click-through by metro over time."* Miami, Austin and NYC lead.
- *"Our FP&A forecast for 2027 doesn't include padel. What does the signal trajectory imply?"* Contrast projected vs external.

**Beat 5: Theme 2, where to open next**
- *"Rank candidate metros (no stores) by the FP&A site model."* Austin, Charlotte, San Antonio.
- *"Now rank them by growth in search, registrations, ad click-through and our own online sales."* Nashville, Austin, Raleigh.
- *"Why does Las Vegas look good on search but not on registrations?"* The trap.

**Beat 6: Publish.** Ask Golden to write the narrative and export it to Slides: *"Build a 5-slide readout for the leadership team."*

## Iteration knobs
All story levers are in `generator/scenario.py`: which metros have the pickleball gap, padel hotspots, per-metro boom growth, the Las Vegas search inflation, the World Cup bump, and so on. Change a knob, then re-run `python3 generator/generate.py && python3 generator/check_story.py`.
