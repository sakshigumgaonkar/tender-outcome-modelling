"""
src/extractors.py
-----------------
Keyword-extraction functions that derive structured fields from
free-text tender titles and organisation hierarchy strings.

Functions
---------
extract_mineral           : Return first mineral keyword found in a tender title.
extract_state_from_title  : Return first Indian state name found in a tender title.
extract_state_from_org    : Infer state from an eProcure/eTender org hierarchy string.
"""

import re
import numpy as np
import pandas as pd


# ── Reference Lists ───────────────────────────────────────────────────────────

MINERALS = [
    'Iron', 'Coal', 'Limestone', 'Bauxite', 'Manganese', 'Copper',
    'Gold', 'Chromite', 'Dolomite', 'Graphite', 'Silica', 'Quartz',
    'Granite', 'Marble', 'Gypsum',
]

STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar',
    'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh',
    'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra',
    'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
    'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
    'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    # Union Territories that commonly appear in tender data
    'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Puducherry', 'Chandigarh',
    'Andaman and Nicobar Islands', 'Dadra and Nagar Haveli',
]

# City-to-state mapping for inferring state from eProcure/eTender
# organisation hierarchy strings, which encode city names but not states.
# Source: cities observed in the actual portal data.
CITY_TO_STATE = {
    'Shillong'      : 'Meghalaya',
    'Jaipur'        : 'Rajasthan',
    'Hyderabad'     : 'Telangana',
    'Bhubaneswar'   : 'Odisha',
    'Bhubhaneswar'  : 'Odisha',      # alternate spelling observed in source data
    'Angul'         : 'Odisha',
    'Damanjodi'     : 'Odisha',
    'Kalpakkam'     : 'Tamil Nadu',
    'Mumbai'        : 'Maharashtra',
    'Visakhapatnam' : 'Andhra Pradesh',
    'Vizag'         : 'Andhra Pradesh',
    'Kolkata'       : 'West Bengal',
    'New Delhi'     : 'Delhi',
}


# ── Extraction Functions ──────────────────────────────────────────────────────

def extract_mineral(text) -> str:
    """
    Return the first mineral name found in a tender title, or NaN.

    Performs a case-insensitive substring search against the MINERALS list.
    Returns the first match in list order (not position in text).

    Parameters
    ----------
    text : str | NaN
        Tender title / work description.

    Returns
    -------
    str | NaN
        Matched mineral name (title-case, as defined in MINERALS), or NaN.

    Examples
    --------
    >>> extract_mineral("Core drilling for iron ore exploration in Jharkhand")
    'Iron'
    >>> extract_mineral("Supply of drilling equipment")
    nan
    """
    if pd.isna(text):
        return np.nan

    text_lower = str(text).lower()

    for mineral in MINERALS:
        if mineral.lower() in text_lower:
            return mineral

    return np.nan


def extract_state_from_title(text) -> str:
    """
    Return the first Indian state (or UT) name found in a tender title, or NaN.

    Used as a fallback when state could not be inferred from the
    organisation hierarchy string (Notebook 01).

    Parameters
    ----------
    text : str | NaN
        Tender title / work description.

    Returns
    -------
    str | NaN
        Matched state/UT name (as defined in STATES), or NaN.

    Notes
    -----
    Only the first match is returned. Tenders spanning multiple states
    are assigned the first state mentioned in the title.

    Examples
    --------
    >>> extract_state_from_title("Geological survey in Rajasthan block area")
    'Rajasthan'
    """
    if pd.isna(text):
        return np.nan

    text_lower = str(text).lower()

    for state in STATES:
        if state.lower() in text_lower:
            return state

    return np.nan


def extract_state_from_org(org) -> str:
    """
    Infer a state name from an eProcure / eTender organisation hierarchy string.

    Organisation strings use '||' as a hierarchy separator, for example:
        "Ministry of Mines || Geological Survey of India || Shillong Office"

    This function checks the deepest (most specific) level first, then
    falls back to the full string, matching against CITY_TO_STATE.

    Parameters
    ----------
    org : str | NaN
        Raw organisation hierarchy string from eProcure or eTender.

    Returns
    -------
    str | None
        Matched state name, or None if no known city was found.

    Examples
    --------
    >>> extract_state_from_org("Ministry || GSI || Bhubaneswar Office")
    'Odisha'
    """
    if pd.isna(org):
        return None

    # Try the most specific (last) hierarchy level first
    last_part = str(org).split('||')[-1]

    for city, state in CITY_TO_STATE.items():
        if re.search(rf'\b{re.escape(city)}\b', last_part, flags=re.IGNORECASE):
            return state

    # Fall back to full organisation string
    for city, state in CITY_TO_STATE.items():
        if re.search(rf'\b{re.escape(city)}\b', str(org), flags=re.IGNORECASE):
            return state

    return None
