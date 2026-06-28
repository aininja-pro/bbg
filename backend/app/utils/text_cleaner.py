"""Text cleaning helpers for spreadsheet import fields."""
import math
import re
import unicodedata
from typing import Any

# Strip characters that are not typical in US street addresses.
_ADDRESS_DISALLOWED = re.compile(r"[^A-Za-z0-9\s#.,\-/']")

# Unicode space-like characters often pasted from Word, PDFs, or web forms.
_UNICODE_SPACE_CHARS = (
    "\u00a0",  # non-breaking space
    "\u200b",  # zero-width space
    "\u200c",  # zero-width non-joiner
    "\u200d",  # zero-width joiner
    "\u2060",  # word joiner
    "\ufeff",  # BOM / zero-width no-break space
    "\u2007",  # figure space
    "\u202f",  # narrow no-break space
)


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and value.strip().lower() in ("", "nan", "none"):
        return True
    return False


def _normalize_unicode_spaces(value: str) -> str:
    for char in _UNICODE_SPACE_CHARS:
        value = value.replace(char, " ")
    return value


def clean_text_field(value: Any) -> Any:
    """Clean address and other free-text fields from spreadsheet imports.

    - Normalizes invisible Unicode spaces to regular spaces
    - Removes control characters and odd symbols
    - Collapses repeated whitespace
    - Preserves common address punctuation (#, -, ., ,, /, ')
    """
    if _is_blank(value):
        return None if value is None else ""

    text = _normalize_unicode_spaces(str(value))
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C")
    text = _ADDRESS_DISALLOWED.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text if text else ""


def clean_zip_postal(value: Any) -> Any:
    """Clean zip/postal values while preserving digits and optional hyphen."""
    if _is_blank(value):
        return None if value is None else ""

    # Leave numeric Excel values alone; later pipeline steps format them.
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and math.isnan(value):
            return None
        return value

    text = _normalize_unicode_spaces(str(value))
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C")
    text = re.sub(r"[^\d\-]", "", text).strip()

    return text if text else ""
