"""
src/schema.py
-------------
Canonical column definitions, rename maps, and reference dictionaries
for the Tender Outcome Modeling pipeline.

Centralising all column names here means a schema change is a
single-file edit — no hunting across six notebooks.

Contents
--------
BID_COLUMNS   : Canonical column order for the bid_data table.
FE_COLUMNS    : Canonical column order for the financial_eval table.
COLUMN_MAPS   : Per-portal raw-column → canonical-name rename dicts.
MINISTRY_MAP  : department_org → ministry backfill lookup.
"""


# ── Canonical column order — bid_data ─────────────────────────────────────────

BID_COLUMNS = [
    'bid_number',
    'title_description',
    'ministry',
    'department_org',
    'contract_period',
    'tender_value',
    'bid_start_date',
    'bid_end_date',
    'award_status',
    'winner',
    'winning_price',
    'website_name',
    'state_name',
]


# ── Canonical column order — financial_eval ───────────────────────────────────

FE_COLUMNS = [
    'bid_number',
    'rank_position',
    'seller',
    'price',
    'status',
]


# ── Per-portal column rename maps ─────────────────────────────────────────────
# Keys   = raw column names in the portal's Excel export
# Values = canonical bid_data column names
# Used in Notebook 01 to rename before any other processing.

COLUMN_MAPS = {
    'gem': {
        'Bid No'              : 'bid_number',
        'Title / Items'       : 'title_description',
        'Ministry'            : 'ministry',
        'Department'          : 'department_org',
        'Contract Period'     : 'contract_period',
        'Estimated Bid Value' : 'tender_value',
        'Bid Start Date'      : 'bid_start_date',
        'Bid End Date'        : 'bid_end_date',
        'Award Status'        : 'award_status',
        'Contract Seller'     : 'winner',
        'Contract Total (₹)'  : 'winning_price',
    },
    'eprocure': {
        'Bid Number'             : 'bid_number',
        'Work Description'       : 'title_description',
        'Organization'           : 'department_org',
        'Contract Period'        : 'contract_period',
        'Tender Value'           : 'tender_value',
        'Published Date'         : 'bid_start_date',
        'Bid Submission End Date': 'bid_end_date',
        'Tender Status'          : 'award_status',
        'Awarded Bidder'         : 'winner',
        'Awarded Value'          : 'winning_price',
    },
    'etender': {
        'Bid Number'             : 'bid_number',
        'Work Description'       : 'title_description',
        'Organization'           : 'department_org',
        'Contract Period'        : 'contract_period',
        'Tender Value'           : 'tender_value',
        'Published Date'         : 'bid_start_date',
        'Bid Submission End Date': 'bid_end_date',
        'Tender Status'          : 'award_status',
        'Awarded Bidder'         : 'winner',
        'Awarded Value'          : 'winning_price',
    },
    'coal_india': {
        'Bid Number'         : 'bid_number',
        'Work Description'   : 'title_description',
        'Organization'       : 'department_org',
        'Contract Period'    : 'contract_period',
        'Estimated Bid Value': 'tender_value',
        'Bid Start Date'     : 'bid_start_date',
        'Bid End Date'       : 'bid_end_date',
        'Tender Status'      : 'award_status',
        'L1 Bidder'          : 'winner',
        'L1 Price (₹)'       : 'winning_price',
    },
}


# ── Ministry backfill lookup ──────────────────────────────────────────────────
# Maps department_org values (from eProcure / eTender) to their parent ministry.
# eProcure and eTender do not include a ministry column in their raw exports.
# Sourced from actual department_org unique values observed in the dataset.

MINISTRY_MAP = {
    'Geological Survey of India'                              : 'Ministry of Mines',
    'National Aluminium Company Limited,NALCO'                : 'Ministry of Mines',
    'Ministry of Mines'                                       : 'Ministry of Mines',
    'Bhabha Atomic Research Centre'                           : 'Department of Atomic Energy',
    'Atomic Minerals Directorate for Exploration and Research': 'Department of Atomic Energy',
    'Damodar Valley Corporation'                              : 'Ministry of Power',
    'Uranium Corporation of India Limited'                    : 'Department of Atomic Energy',
    'Hindustan Copper Limited'                                : 'Ministry of Mines',
    'Oil and Natural Gas Corporation Limited'                 : 'Ministry of Petroleum & Natural Gas',
    'Nuclear Power Corporation Of India Limited'              : 'Department of Atomic Energy',
}
