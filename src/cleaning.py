"""
src/cleaning.py
---------------
Core cleaning functions for company names, prices, and contract durations.
"""

import re
import numpy as np
import pandas as pd


def clean_company_name(name) -> str:
    """
    Normalise a raw company name from a government portal.

    Transformations applied (in order):
      1. Remove MSE Social Category annotations
      2. Remove MII (Make in India) annotations
      3. Remove "Under PMA" suffix
      4. Standardise ALL Pvt/Private + Ltd/Limited variants -> "Private Limited"
         Handles every casing and punctuation combination:
           pvt ltd, Pvt Ltd., PVT. LTD, private limited, PRIVATE LTD, pvt. ltd. etc.
      5. Standardise standalone "Ltd" (not preceded by Private) -> "Limited"
      6. Remove trailing punctuation
      7. Collapse multiple spaces
      8. Title-case

    This function is idempotent: running it twice on an already-cleaned name
    produces the same result, so it is always safe to re-apply.

    Examples
    --------
    >>> clean_company_name("mapp private limited")
    'Mapp Private Limited'
    >>> clean_company_name("MAPP pvt Ltd.")
    'Mapp Private Limited'
    >>> clean_company_name("company Pvt Ltd")
    'Company Private Limited'
    >>> clean_company_name("company Private limited")
    'Company Private Limited'
    """
    if pd.isna(name):
        return name

    name = str(name)

    name = re.sub(r'\(\s*MSE.*?\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\(\s*MII.*?\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\bUnder PMA\b', '', name, flags=re.IGNORECASE)

    # Standardise ALL Pvt/Private + Ltd/Limited combinations -> "Private Limited"
    # Matches regardless of case, spacing, or trailing periods:
    #   pvt ltd | Pvt. Ltd. | PVT LTD | private limited | Private Ltd. | pvt. limited
    name = re.sub(
        r'\b(?:p\.?vt\.?|private)\s*\.?\s*(?:ltd\.?|limited)\b\.?',
        'Private Limited',
        name,
        flags=re.IGNORECASE,
    )

    # Standalone "Ltd" (not already converted above) -> "Limited"
    name = re.sub(r'(?<!Private )\bLtd\.?\b', 'Limited', name, flags=re.IGNORECASE)

    # Remove trailing punctuation left over from abbreviations
    name = re.sub(r'[.,]+$', '', name)

    # Collapse whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    return name.title()


def normalize_name(name) -> str:
    """
    Produce a normalised uppercase key for FK matching (not for display).

    Strips annotations, uppercases, and collapses whitespace.
    Used in competitor analysis and seller master linkage.
    """
    if not isinstance(name, str):
        return ""
    s = name.strip().upper()
    s = re.sub(r'\(\s*MSE\s+SOCIAL\s+CATEGORY\s*:[^)]*\)', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bUNDER\s+PMA\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s{2,}', ' ', s).strip()
    return s


def clean_price(value) -> float:
    """Convert a raw price string or number to float. Returns NaN on failure."""
    if pd.isna(value):
        return np.nan
    cleaned = re.sub(r'[^0-9.]', '', str(value))
    try:
        return float(cleaned)
    except ValueError:
        return np.nan


def contract_to_days(text) -> float:
    """
    Parse a free-text contract duration string into total days.
    1 year = 365 days, 1 month = 30 days.
    Returns NaN if no duration found.
    """
    if pd.isna(text):
        return np.nan

    text = str(text).lower()

    year_match  = re.search(r'(\d+)\s*year',  text)
    month_match = re.search(r'(\d+)\s*month', text)
    day_match   = re.search(r'(\d+)\s*day',   text)

    years  = int(year_match.group(1))  if year_match  else 0
    months = int(month_match.group(1)) if month_match else 0
    days   = int(day_match.group(1))   if day_match   else 0

    total_days = (years * 365) + (months * 30) + days
    return float(total_days) if total_days > 0 else np.nan