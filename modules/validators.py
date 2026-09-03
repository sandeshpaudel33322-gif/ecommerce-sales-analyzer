"""
validators.py
--------------
Small, focused input-validation helpers used by the interactive CLI
(main.py) to satisfy the "Invalid-input and edge-case testing"
requirement. Keeping these separate from main.py makes them easy to
unit test in isolation (see tests/test_validators.py).
"""

from typing import Optional


def validate_menu_choice(raw_input: str, valid_choices) -> Optional[str]:
    """
    Validate a menu selection. Returns the cleaned choice if valid,
    otherwise None (caller is responsible for re-prompting).

    Handles edge cases: empty input, surrounding whitespace, and
    non-numeric junk typed into a numeric menu.
    """
    if raw_input is None:
        return None
    cleaned = raw_input.strip()
    if cleaned in valid_choices:
        return cleaned
    return None


def validate_non_empty_string(raw_input: str) -> Optional[str]:
    """Returns the trimmed string if non-empty, else None."""
    if raw_input is None:
        return None
    cleaned = raw_input.strip()
    return cleaned if cleaned else None


def validate_positive_int(raw_input: str) -> Optional[int]:
    """Parses `raw_input` as a positive integer, or returns None on any failure."""
    if raw_input is None:
        return None
    cleaned = raw_input.strip()
    if not cleaned:
        return None
    try:
        value = int(cleaned)
    except ValueError:
        return None
    return value if value > 0 else None


def validate_date_string(raw_input: str) -> Optional[str]:
    """
    Confirms `raw_input` looks like a YYYY-MM-DD date and is a real
    calendar date (rejects e.g. 2026-13-40). Returns the cleaned string
    or None.
    """
    from datetime import datetime
    if raw_input is None:
        return None
    cleaned = raw_input.strip()
    try:
        datetime.strptime(cleaned, "%Y-%m-%d")
    except ValueError:
        return None
    return cleaned


def validate_yes_no(raw_input: str) -> Optional[bool]:
    """Accepts y/yes/n/no (any case). Returns True/False, or None if unrecognised."""
    if raw_input is None:
        return None
    cleaned = raw_input.strip().lower()
    if cleaned in ("y", "yes"):
        return True
    if cleaned in ("n", "no"):
        return False
    return None
