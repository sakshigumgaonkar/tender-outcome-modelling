"""
config.py
---------
Central configuration for the Tender Outcome Modeling project.
Edit only this file to adapt the pipeline to a different company or directory layout.
"""

from pathlib import Path

ROOT_DIR       = Path(__file__).resolve().parent
DATA_RAW       = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"

# ── Company of interest ───────────────────────────────────────────────────────
FOCUS_COMPANY_NAME = "Bhushilp Mines And Minerals Private Limited"
FOCUS_COMPANY_ABBR = "BMMPL"

# ── Raw input filenames ───────────────────────────────────────────────────────
RAW_FILES = {
    "gem"       : DATA_RAW / "gem_bid_status_detail.xlsx",
    "eprocure"  : DATA_RAW / "eprocure_result_tenders_detail.xlsx",
    "etender"   : DATA_RAW / "etenders_result_tenders_detail.xlsx",
    "coal_india": DATA_RAW / "coal_india_tenders_details.xlsx",
}

# ── Processed output filenames ────────────────────────────────────────────────
PROCESSED_FILES = {
    # Per-portal outputs  (Notebook 01)
    "gem_bids"          : DATA_PROCESSED / "gem_bid_data.xlsx",
    "gem_fe"            : DATA_PROCESSED / "gem_fe.xlsx",
    "eprocure_bids"     : DATA_PROCESSED / "eprocure_bid_data.xlsx",
    "eprocure_fe"       : DATA_PROCESSED / "eprocure_financial_eval.xlsx",
    "etender_bids"      : DATA_PROCESSED / "etender_bid_data.xlsx",
    "etender_fe"        : DATA_PROCESSED / "etender_financial_eval.xlsx",
    "coal_india_bids"   : DATA_PROCESSED / "CoalIndia_bid_data.xlsx",
    "coal_india_fe"     : DATA_PROCESSED / "CoalIndia_financial_eval.xlsx",

    # Merged outputs  (Notebook 02)
    "merged_bids"       : DATA_PROCESSED / "merged_bid_data.xlsx",
    "merged_fe"         : DATA_PROCESSED / "merged_financial_evaluation.xlsx",

    # Feature-engineered outputs  (Notebook 03)
    "featured_bids"     : DATA_PROCESSED / "final_bid_data.xlsx",

    # Seller master  (Notebook 04)
    "company_info"      : DATA_PROCESSED / "company_info.xlsx",
    "final_fe"          : DATA_PROCESSED / "final_FE.xlsx",

    # Competitor analysis  (Notebook 05)
    "competitor_analysis": DATA_PROCESSED / "final_competitor_analysis.xlsx",
}
