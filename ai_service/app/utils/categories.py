"""Donation-category helpers (the mapping lives in donation_categories.json and is editable)."""
import json
from functools import lru_cache
from pathlib import Path

_FILE = Path(__file__).with_name("donation_categories.json")


@lru_cache
def _cfg():
    return json.loads(_FILE.read_text())


def donation_categories():
    return list(_cfg()["donation_categories"])


def normalize_category(name: str) -> str:
    """Accept either a donation category or a Food-101-style dish category (e.g. 'meat_dish')."""
    n = name.strip().lower()
    if n in _cfg()["donation_categories"] or n == "any":
        return n
    return _cfg()["dish_to_donation"].get(n, n)
