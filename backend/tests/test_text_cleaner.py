"""Tests for spreadsheet text cleaning helpers."""
import math

import pytest

from app.utils.text_cleaner import clean_text_field, clean_zip_postal


class TestCleanTextField:
    def test_strips_leading_and_trailing_spaces(self):
        assert clean_text_field("  123 Main St  ") == "123 Main St"

    def test_collapses_internal_whitespace(self):
        assert clean_text_field("123   Main    St") == "123 Main St"

    def test_normalizes_non_breaking_space(self):
        assert clean_text_field("123\u00a0Main\u00a0St") == "123 Main St"

    def test_removes_zero_width_characters(self):
        assert clean_text_field("123\u200bMain\u200bSt") == "123 Main St"

    def test_preserves_common_address_punctuation(self):
        assert clean_text_field("Apt 4, 123 Main St.") == "Apt 4, 123 Main St."
        assert clean_text_field("1234-56 Oak/Elm Dr") == "1234-56 Oak/Elm Dr"

    def test_removes_hash_character(self):
        assert clean_text_field("#1200 Central Ave SE") == "1200 Central Ave SE"
        assert clean_text_field("Albuquerque#") == "Albuquerque"
        assert clean_text_field("Apt #4") == "Apt 4"

    def test_removes_weird_symbols(self):
        assert clean_text_field("123 Main St™") == "123 Main St"
        assert clean_text_field("123 Main St★") == "123 Main St"
        assert clean_text_field("%$8200 Menaul Blvd NE") == "8200 Menaul Blvd NE"

    def test_handles_blank_values(self):
        assert clean_text_field(None) is None
        assert clean_text_field("") == ""
        assert clean_text_field("   ") == ""
        assert clean_text_field(float("nan")) == ""

    def test_converts_numeric_job_codes(self):
        assert clean_text_field(12345) == "12345"


class TestCleanZipPostal:
    def test_preserves_numeric_excel_values(self):
        assert clean_zip_postal(49001) == 49001
        assert clean_zip_postal(49001.0) == 49001.0

    def test_cleans_string_zip_values(self):
        assert clean_zip_postal(" 49001 ") == "49001"
        assert clean_zip_postal("49001\u00a0") == "49001"

    def test_preserves_zip_plus_four(self):
        assert clean_zip_postal("49001-1234") == "49001-1234"

    def test_removes_non_numeric_junk_from_strings(self):
        assert clean_zip_postal("49001™") == "49001"

    def test_handles_blank_values(self):
        assert clean_zip_postal(None) is None
        assert clean_zip_postal("") == ""
        assert clean_zip_postal(float("nan")) == ""
