# Tender Outcome Modeling

A professional end-to-end data pipeline for collecting, standardising, and analysing
Indian government procurement tender data across four portals: **GEM**, **eProcure**,
**eTender India**, and **Coal India**. Produces a unified tender dataset, a seller master,
and a competitive intelligence report centred on a configurable company of interest.

---

## Project Overview

Indian government procurement is distributed across multiple portals with inconsistent
schemas, free-text fields, and encoding variations. This project standardises data from
four portals into a single analytical layer and answers questions such as:

- Who are the most active bidders in the mining and minerals sector?
- What is the win rate of any given company across portals and over time?
- Which competitors most frequently compete in the same tenders?
- What is the conditional probability of winning a tender when competing against
  a specific company?

---

## Data Sources

| Portal | Description | Unique Characteristics |
|--------|-------------|------------------------|
| [GEM](https://gem.gov.in) | Government e-Marketplace | All bidders in a single pipe-delimited cell per tender; RA conversion logic |
| [eProcure](https://eprocure.gov.in) | Central Public Procurement Portal | `\|\|`-delimited org hierarchy; ministry not included in export |
| [eTenders India](https://etenders.gov.in) | eTenders portal | State-level procurement; no ministry column |
| [Coal India](https://coalindiatenders.nic.in) | Coal India Limited | L1 Bidder as winner field; ministry always "Ministry of Coal" |

Raw files are expected at `data/raw/`. They are **not committed** to version control
(see `.gitignore`).

---

## Data Pipeline

```
data/raw/                     ← Raw Excel exports from each portal
      │
      ▼
01_portal_ingestion.ipynb     ← Standardise each portal → canonical schema
      │                          8 per-portal Excel files
      ▼
02_data_merging.ipynb         ← Concatenate portals; quality gates; ministry fill
      │                          merged_bid_data, merged_financial_eval
      ▼
03_feature_engineering.ipynb  ← Title backfill; mineral/state/meterage extraction;
      │                          L1 winner imputation; tender_value backfill
      │                          featured_bid_data
      ▼
04_seller_master.ipynb        ← Build company_info; assign company_ids; link FKs
      │                          company_info, final_financial_eval
      ▼
05_competitor_analysis.ipynb  ← Head-to-head stats; conditional win probabilities
      │                          competitor_analysis
      ▼
06_eda_and_quality.ipynb      ← Data quality report; distributions; visual insights
```

---

## Folder Structure

```
tender-outcome-modeling/
│
├── README.md
├── requirements.txt
├── .gitignore
├── config.py                        ← Central config: company name, file paths
│
├── data/
│   ├── raw/                         ← Raw input files (gitignored)
│   └── processed/                   ← Pipeline outputs (gitignored)
│
├── src/                             ← Reusable utility modules
│   ├── __init__.py
│   ├── cleaning.py                  ← clean_company_name, normalize_name,
│   │                                   clean_price, contract_to_days
│   ├── parsers.py                   ← parse_date, parse_bidders,
│   │                                   extract_drilling_meterage
│   ├── extractors.py                ← extract_mineral, extract_state_from_title,
│   │                                   extract_state_from_org, CITY_TO_STATE
│   └── schema.py                    ← BID_COLUMNS, FE_COLUMNS, COLUMN_MAPS,
│                                       MINISTRY_MAP
│
└── notebooks/
    ├── 01_portal_ingestion.ipynb
    ├── 02_data_merging.ipynb
    ├── 03_feature_engineering.ipynb
    ├── 04_seller_master.ipynb
    ├── 05_competitor_analysis.ipynb
    └── 06_eda_and_quality.ipynb
```

---

## Notebook Reference

| # | Notebook | Inputs | Key Outputs |
|---|----------|--------|-------------|
| 01 | Portal Ingestion | 4 raw Excel files | 8 per-portal Excel files |
| 02 | Data Merging | 8 per-portal files | `merged_bid_data.xlsx`, `merged_financial_eval.xlsx` |
| 03 | Feature Engineering | `merged_bid_data.xlsx` + raw files | `featured_bid_data.xlsx` |
| 04 | Seller Master | `featured_bid_data.xlsx`, `merged_financial_eval.xlsx` | `company_info.xlsx`, `final_financial_eval.xlsx` |
| 05 | Competitor Analysis | `featured_bid_data.xlsx`, `final_financial_eval.xlsx`, `company_info.xlsx` | `competitor_analysis.xlsx` |
| 06 | EDA & Quality | All processed files | Visual report (no new files) |

---

## Data Integrity Safeguards

`bid_number` is the primary key used to join `bid_data`, `financial_eval`, and the
competitor analysis throughout this pipeline. **If `bid_number` is ever non-unique,
`winner` can silently get misaligned to the wrong tender** — the price stays correct
but the company name attached to it does not, because pandas operations that key on
a non-unique index don't error, they just pick a row.

This was caught in practice: a tender appeared with the correct winning price but the
wrong winner name, traced back to duplicate `bid_number` rows surviving the initial
merge (re-scraped or re-published tenders with conflicting `winner` values).

To prevent this from recurring silently, the pipeline now enforces:

| Notebook | Safeguard |
|----------|-----------|
| 02 — Data Merging | Detects duplicate `bid_number`s after concatenation; flags any where `winner` disagrees across duplicates; resolves by keeping the most recently published row |
| 02 — Data Merging | Deduplicates `financial_eval` on `(bid_number, seller)` so no bidder is double-counted |
| 03, 04, 05 | Each notebook asserts `bid_data['bid_number'].is_unique` immediately after loading, before any `.map()` or `.set_index()` call — fails loudly instead of corrupting data silently |

If any of these assertions fail, re-run Notebook 02 before continuing — do not skip
straight to a later notebook on stale output files.

---

## Feature Engineering Summary

| Feature | Source | Method |
|---------|--------|--------|
| `contract_period` | Raw contract duration string | Regex → days (1 yr = 365d, 1 mo = 30d) |
| `state_name` | Organisation hierarchy / title | City→state map; state keyword list |
| `mineral_name` | `title_description` | Keyword search — 15-mineral reference list |
| `drilling_meterage` | `title_description` | 3-tier regex: direct qty → BH×depth → generic |
| `winner` (imputed) | `financial_eval` L1 rank | Backfill where awarded bidder not published |
| `winning_price` (imputed) | `financial_eval` L1 price | Same imputation logic |
| `tender_value` (backfill) | `financial_eval` min price | Fill remaining blanks from minimum bid |
| `ministry` (backfill) | `department_org` | `MINISTRY_MAP` dict in `src/schema.py` |
| `winner_company_id` | `winner`, `company_info` | Normalised name → FK join |

---

## Configuration

The focus company for competitive analysis is set in `config.py`:

```python
FOCUS_COMPANY_NAME = "Bhushilp Mines And Minerals Private Limited"
FOCUS_COMPANY_ABBR = "BMMPL"
```

Change these two values and re-run Notebook 05 to generate the full
competitive analysis relative to any other company in the dataset.

---

## Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/your-username/tender-outcome-modeling.git
cd tender-outcome-modeling

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place raw data files in data/raw/
#    (filenames must match RAW_FILES in config.py)

# 4. Run notebooks in order
jupyter notebook notebooks/01_portal_ingestion.ipynb
```

---

## Outputs Generated

| File | Description |
|------|-------------|
| `gem_bid_data.xlsx` | GEM tenders in canonical schema |
| `eprocure_bid_data.xlsx` | eProcure tenders in canonical schema |
| `etender_bid_data.xlsx` | eTender tenders in canonical schema |
| `coal_india_bid_data.xlsx` | Coal India tenders in canonical schema |
| `merged_bid_data.xlsx` | All portals merged, quality-filtered |
| `featured_bid_data.xlsx` | Final enriched tender table |
| `company_info.xlsx` | Master company reference table |
| `final_financial_eval.xlsx` | Bidder rankings with company FK |
| `competitor_analysis.xlsx` | Head-to-head stats vs BMMPL |

---

## Analytics Dashboard (Power BI)

The processed outputs from this pipeline feed directly into an internal Power BI dashboard
(MTIS Dashboard), accessible to organisation members only. The dashboard provides interactive
filtering and drill-through across all pipeline outputs.

The dashboard is organised into **5 report pages**:

---

### Page 1 — Keyword Bid Explorer
Search any keyword (e.g. "mass production", "core drilling") and instantly see all matching
tenders, their winners, winning prices, and participating companies with rank and quoted price.
Includes a KPI card comparing total winning price against tender value estimate.

![Keyword Bid Explorer](docs/screenshots/01_keyword_bid_explorer.png)

---

### Page 2 — Keyword Summary
Aggregated view for a given keyword search: total bid count, sum of tender value, bids over
time (dual-axis line chart), ministry distribution (stacked bar), and winning price by seller
(bar chart). Useful for understanding market size and competitive density for any work category.

![Keyword Summary](docs/screenshots/02_keyword_summary.png)

---

### Page 3 — Bid Detail Drill-Through
Single-tender drill-through page. Shows the bid winner prominently, tender description,
KPI cards (winning price vs tender value, contract period, bid start date, mineral, state,
ministry, department), and a bar chart of all participating sellers ranked by quoted price.

![Bid Detail](docs/screenshots/03_bid_detail.png)

---

### Page 4 — Ministry Overview
Filter by ministry to see total bids, sum of tender value, bids over time (2019–2026),
department breakdown (pie chart with counts), and top winners by total winning price.
Shown here for Ministry of Mines: 817 bids, ₹5,348 Cr total tender value.

![Ministry Overview](docs/screenshots/04_ministry_overview.png)

---

### Page 5a — Company Profile (Activity)
Select any company from the dropdown to see their full bidding history:
total bids applied, bids won, L2/L3 near-miss rankings, total revenue won,
ministry-wise bid distribution (stacked bar by rank), bid amounts for won tenders,
and revenue trend over the years with a trendline.

![Company Profile Activity](docs/screenshots/05a_company_profile_activity.png)

---

### Page 5b — Company Profile (Pricing Analytics)
Deep-dive pricing statistics for the selected company: average bidded price, median,
standard deviation, max, min, average margin %, contractor win rate, and average per
meter rate. Charts include winner vs runner-up price gap per bid, contract period by
bid, and tender value vs winning price comparison.

![Company Profile Pricing](docs/screenshots/05b_company_profile_pricing.png)

---

### Page 5c — Competitive Bid Overview
Head-to-head view for the selected company vs BMMPL. KPI cards show total bids applied,
bids won, common bids with BMMPL, bids won against BMMPL, bids BMMPL won, and bids where
both lost. The main visual is a custom proportional bar showing total applied vs won,
with the common-bid window highlighted in red and colour-coded by outcome.

![Competitive Bid Overview](docs/screenshots/05c_competitive_bid_overview.png)

---

> **Note:** The Power BI file (`.pbix`) is not included in this repository as the dashboard
> is hosted internally and requires organisational credentials to access.
> Screenshots above are for documentation purposes.

---

## Future Improvements

- [ ] **NLP title classification** — fine-tuned classifier to categorise tenders
  by work type (drilling, surveying, supply, civil works)
- [ ] **Cross-portal duplicate detection** — fuzzy matching to identify the same
  tender published on multiple portals
- [ ] **Price analysis** — L1/L2 price ratio; discount-to-estimate distribution
  by ministry and work type
- [ ] **Temporal win modelling** — track how competitive dynamics shift year-over-year
- [ ] **Expanded mineral coverage** — add synonyms and regional spelling variants
