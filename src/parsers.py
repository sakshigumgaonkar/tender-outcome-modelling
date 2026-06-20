"""
src/parsers.py
--------------
Parsing functions for dates, GEM pipe-delimited bidder strings,
and drilling meterage extraction from tender titles.

Functions
---------
parse_date                : Parse a date string using Indian portal date formats.
parse_bidders             : Explode a GEM pipe-delimited bidder string into rows.
extract_drilling_meterage : Extract total drilling metres from a tender title.
"""

import re
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Optional


# ── Date Parsing ──────────────────────────────────────────────────────────────

# Ordered list of date formats found in Indian government portal exports.
# Tried in sequence; the first match wins. Using an explicit list avoids the
# ambiguity and performance overhead of dateutil inference.
_DATE_FORMATS = [
    '%d-%m-%Y',   # 10-03-2025  (most common in GEM / Coal India)
    '%d/%m/%Y',   # 10/03/2025
    '%Y-%m-%d',   # 2025-03-10  (ISO, sometimes in eProcure exports)
    '%d %b %Y',   # 10 Mar 2025
    '%d %B %Y',   # 10 March 2025
    '%d-%b-%Y',   # 10-Mar-2025
    '%d-%B-%Y',   # 10-March-2025
]


def parse_date(value) -> Optional[datetime]:
    """
    Parse a date string using a prioritised list of Indian portal date formats.

    Parameters
    ----------
    value : str | datetime | None
        Raw date value from source data.

    Returns
    -------
    datetime | pd.NaT
        Parsed datetime object, or pd.NaT if no format matched.

    Examples
    --------
    >>> parse_date("10-03-2025")
    datetime.datetime(2025, 3, 10, 0, 0)
    >>> parse_date("10 Mar 2025")
    datetime.datetime(2025, 3, 10, 0, 0)
    """
    if pd.isna(value):
        return pd.NaT

    value = str(value).strip()

    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return pd.NaT


# ── GEM Bidder String Parsing ─────────────────────────────────────────────────

def parse_bidders(bid_number: str, raw) -> list:
    """
    Explode a GEM pipe-delimited bidder string into individual row dicts.

    GEM encodes all bidders for a single tender in one cell using the format:
        Rank | Seller Name | Price | Status
    Multiple bidders are separated by newlines or semicolons.

    Parameters
    ----------
    bid_number : str
        The tender identifier — used to key each returned row.
    raw : str | NaN
        Raw pipe-delimited bidder string from the GEM source file
        (column: "All Bidders (Rank | Seller | Price | Status)").

    Returns
    -------
    list[dict]
        One dict per valid bidder row with keys:
        bid_number, rank_position, seller, price, status.
        Malformed entries (fewer than 4 pipe-separated fields) are
        silently skipped.

    Examples
    --------
    >>> rows = parse_bidders("GEM/2024/B/123", "L1 | ABC Mining Pvt Ltd | 500000 | Accepted")
    >>> rows[0]['rank_position']
    'L1'
    """
    from src.cleaning import clean_price

    rows = []
    if pd.isna(raw):
        return rows

    for entry in re.split(r'\n|;', str(raw)):
        parts = [p.strip() for p in entry.split('|')]
        if len(parts) < 4:
            continue
        rows.append({
            'bid_number'   : bid_number,
            'rank_position': parts[0],
            'seller'       : parts[1],
            'price'        : clean_price(parts[2]),
            'status'       : parts[3],
        })

    return rows


# ── Drilling Meterage Extraction ──────────────────────────────────────────────

def extract_drilling_meterage(title) -> float:
    """
    Extract total drilling meterage quantity from a tender title / work description.

    Uses a three-tier priority cascade:

    Tier 1 — Direct drilling quantity
        Patterns like "27060m core drilling", "core drilling of 500 meters",
        "quantity 1200m", "surface drilling 800m".

    Tier 2 — Boreholes × depth formula
        Patterns like "80 boreholes upto 200m" → 80 × 200 = 16000.
        Requires both a borehole count AND a depth qualifier (upto / maximum / max).

    Tier 3 — Generic drilling quantity (fallback)
        Patterns like "drilling work of 40000m", "drilling of 27060m".

    Parameters
    ----------
    title : str | NaN
        Tender title / work description string.

    Returns
    -------
    float | NaN
        Extracted meterage as a float, or NaN if none of the tiers matched.

    Examples
    --------
    >>> extract_drilling_meterage("Core Drilling of 27060m in Jharkhand")
    27060.0
    >>> extract_drilling_meterage("80 Boreholes upto 200 meters depth")
    16000.0
    >>> extract_drilling_meterage("Drilling work of 40,000m")
    40000.0
    """
    if pd.isna(title):
        return np.nan

    text = str(title).lower()

    # ── Tier 1: Direct drilling quantity ──────────────────────────────────────
    direct_patterns = [
        r'(\d[\d,]*)\s*(?:m|meter|meters)\s*(?:core\s+)?drilling',
        r'core\s+drilling.*?(\d[\d,]*)\s*(?:m|meter|meters)',
        r'(\d[\d,]*)\s*(?:m|meter|meters)\s*surface.*?drilling',
        r'(\d[\d,]*)\s*(?:m|meter|meters)\s*of\s*\d+\s*mm\s*dia\s*production\s*drilling',
        r'quantity\s*(\d[\d,]*)\s*(?:m|meter|meters)',
    ]

    for pattern in direct_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(',', ''))

    # ── Tier 2: Boreholes × depth ─────────────────────────────────────────────
    bh_match    = re.search(r'(\d+)\s*(?:boreholes|bhs|bh)\b', text, re.IGNORECASE)
    depth_match = re.search(
        r'(?:upto|up to|maximum|max)\s*(\d+)\s*(?:m|meter|meters)',
        text, re.IGNORECASE
    )

    if bh_match and depth_match:
        boreholes = int(bh_match.group(1))
        depth     = int(depth_match.group(1))
        return float(boreholes * depth)

    # ── Tier 3: Generic drilling quantity (fallback) ──────────────────────────
    generic = re.search(r'drilling.*?(\d[\d,]*)\s*(?:m|meter|meters)', text, re.IGNORECASE)
    if generic:
        return float(generic.group(1).replace(',', ''))

    return np.nan
