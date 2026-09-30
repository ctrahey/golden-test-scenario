# Golden Analytics demo: Kestrel Sports Co.

This repo holds a fictional sporting-goods retailer's internal, external and forecast data. Use it to walk through [Golden Analytics](https://goldenanalytics.com/) against Redshift.

- **The story and demo script:** [`docs/STORY.md`](docs/STORY.md). Start here.
- **Story knobs:** [`generator/scenario.py`](generator/scenario.py)

## Quickstart

```bash
python3 generator/generate.py      # ~2s, stdlib only -> data/<schema>/<table>.csv (~20 MB)
python3 generator/check_story.py   # loads the CSVs into SQLite and prints every number the demo relies on
```

### Option A: Redshift Serverless (about 10 minutes to stand up)
```bash
export AWS_PROFILE=<your-profile>                     # scripts use the standard AWS CLI env
GOLDEN_CIDR=<golden egress ip>/32 ./aws/deploy.sh   # VPC + S3 + IAM + secrets + Redshift Serverless (8 RPU)
./aws/load.sh                                        # sync CSVs to S3, create tables, COPY, create golden_ro user
./aws/teardown.sh                                    # when done
```
`load.sh` prints the host and database, plus the command that fetches the `golden_ro` password. `golden_ro` is SELECT-only on all four schemas.

Notes:
- Redshift Serverless bills per RPU-second only while queries run. At 8 RPU that's roughly $3 per active hour.
- If you don't know Golden's egress IPs, `GOLDEN_CIDR=0.0.0.0/0` works for a throwaway stack. The password is still required.

### Option B: skip AWS
Golden accepts CSV uploads directly. Run the generator, then upload the 10 files in `data/`. The table names and join keys are the same either way.

## Data model

Every fact table joins on `metro_id` (to `ref.dim_metro`) and `sport_id` (to `ref.dim_sport`).

| Schema | Meaning | Tables |
|---|---|---|
| `ref` | Shared reference data | `dim_metro` (31 metros, `has_kestrel_store`), `dim_sport` (15 sports, `carried_by_kestrel`) |
| `internal` | Kestrel first-party **actuals** | `sales_monthly`, `dim_product`, `top_trending_products_quarterly`, `ad_interest_program_weekly` (a marketing interest signal) |
| `external` | Paid third-party data | `search_trends_weekly` (Querylytics), `league_registrations` (partner leagues) |
| `forecast` | FP&A **projections** | `sales_baseline_monthly` (Sep 2026 – Dec 2027, p10/p50/p90), `site_selection_candidates` |

Each table also carries a Redshift `COMMENT` that describes its provenance and coverage. See `sql/01_create_tables.sql`.

## Layout
```
docs/STORY.md             narrative, themes, beat-by-beat demo prompts
generator/scenario.py     story knobs (metros, sports, trends, gaps, hotspots)
generator/generate.py     data generator (deterministic seed)
generator/check_story.py  verifies the story shows up in the data
sql/                      Redshift DDL, COPY, read-only user
aws/                      CloudFormation template + deploy/load/teardown scripts
data/                     generated CSVs (gitignored; run the generator)
```
