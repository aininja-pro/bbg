"""Checks for new rule columns and the column G address-type headings."""
import pandas as pd

from app.services.data_enricher import DataEnricher
from app.services.data_transformer import (
    DataTransformer,
    is_base_data_column,
    mark_column_g_as_address_type,
)


class FakeRule:
    """Stand-in for a saved rule. The enricher only reads these fields."""

    def __init__(self, config):
        self.rule_type = "if_then_else"
        self.enabled = True
        self.config = config


def test_column_g_headings_become_address_type():
    """Residential, Multi-Unit, and Single Family/Multi-unit are the same column."""
    transformer = DataTransformer()
    frame = pd.DataFrame({
        "Residential": ["", "Townhome"],
        "Multi-Unit": ["Duplex", ""],
        "Single Family/Multi-unit": ["Single", "Multi"],
        "Single Family / Multi-unit": ["A", ""],
    })

    # Run each heading through the renamer on its own so they do not collide.
    for original in list(frame.columns):
        one_column = frame[[original]].copy()
        renamed = transformer.standardize_columns(one_column)
        assert list(renamed.columns) == ["address_type"]

    # A blank cell becomes RESIDENTIAL. A filled cell is kept.
    residential = transformer.standardize_columns(frame[["Residential"]].copy())
    assert residential["address_type"].tolist()[0] == "RESIDENTIAL"
    assert residential["address_type"].tolist()[1] == "Townhome"


def test_renaming_column_g_still_makes_it_the_address_type_column():
    """Column G is address type even when the heading is not one we listed."""
    headers = [
        "Date",
        "Job Code",
        "Address",
        "City",
        "State",
        "Zip",
        "Dwelling Type",
    ]
    renamed = mark_column_g_as_address_type(headers)
    assert renamed[6] == "address_type"
    assert renamed[0] == "Date"
    # The other columns are left alone.
    assert renamed[5] == "Zip"


def test_repeated_product_headings_do_not_crash_unpivot():
    """Two columns with the same name must not stop the file from processing.

    Column G is kept by position, even when the heading is a new phrase.
    """
    transformer = DataTransformer()
    frame = pd.DataFrame([[
        "9/30/26", "J1", "16784 Wilden Dr", "Clive", "IA", "50235",
        "RESIDENTIAL", 1, 2, 4,
    ]], columns=[
        "Date", "JobCode", "Address", "City", "State", "Zip",
        "Residential or Multi-Unit",
        "Certainteed 3 Tab Shingles  - Single Family",
        "Certainteed 3 Tab Shingles  - Single Family",
        "Humidifier",
    ])
    result = transformer.unpivot_products(
        frame,
        {10: {"product_id": "5419", "distributor": "Test"}},
        {"bbg_member_id": "1399", "member_name": "Covenant"},
    )
    assert result.iloc[0, 6] == "RESIDENTIAL"
    assert result["quantity"].tolist() == [4]


def test_column_g_is_kept_as_home_data():
    assert is_base_data_column("Residential")
    assert is_base_data_column("Multi-Unit")
    assert is_base_data_column("Single Family/Multi-unit")
    assert is_base_data_column("address_type")
    assert not is_base_data_column("Cabinets")


def test_quantity_rule_creates_a_column_and_updates_an_existing_one():
    """If quantity is 2 or more, flag it and set the existing quantity to 1.

    Blank and text values are not treated as zero.
    """
    enricher = DataEnricher(db=None)
    enricher.supplier_rules = [FakeRule({
        "condition": {
            "type": "group",
            "logic": "AND",
            "children": [{
                "type": "condition",
                "field": "quantity",
                "operator": "greater_or_equal",
                "value": "2",
                "comparison_type": "number",
                "treat_blank_as_zero": False,
            }],
        },
        "then_actions": [
            {
                "type": "set_value",
                "field": "Multiple Quantity",
                "value": "True",
                "output_type": "boolean",
                "else_enabled": True,
                "else_value": "False",
                "else_output_type": "boolean",
            },
            {
                "type": "set_value",
                "field": "quantity",
                "value": "1",
                "output_type": "number",
            },
        ],
    })]

    frame = pd.DataFrame({"quantity": [1, 2, None, "Hide"]})
    result = enricher.apply_flexible_rules(frame)

    assert result["Multiple Quantity"].tolist() == [False, True, False, False]
    # Only the row that matched is changed to 1. The others stay as they were.
    assert result["quantity"].tolist()[0] == 1
    assert result["quantity"].tolist()[1] == 1
    assert pd.isna(result["quantity"].tolist()[2])
    assert result["quantity"].tolist()[3] == "Hide"


def test_new_column_is_left_out_when_the_check_never_passes():
    """Quantity Check > 3 should not add a column when every quantity is 3 or less.

    The column appears only for a row that passes. Rows that fail stay blank.
    """
    enricher = DataEnricher(db=None)
    enricher.supplier_rules = [FakeRule({
        "condition": {
            "type": "condition",
            "field": "quantity",
            "operator": "greater_than",
            "value": "3",
            "comparison_type": "number",
        },
        "then_actions": [{
            "type": "set_value",
            "field": "Quantity Check",
            "value": "True",
            "output_type": "boolean",
        }],
    })]

    no_match = enricher.apply_flexible_rules(pd.DataFrame({"quantity": [1, 2, 3]}))
    assert "Quantity Check" not in no_match.columns

    mixed = enricher.apply_flexible_rules(pd.DataFrame({"quantity": [1, 4]}))
    assert mixed["Quantity Check"].tolist() == ["", True]


def test_blank_number_is_not_zero_unless_the_rule_says_so():
    enricher = DataEnricher(db=None)

    assert enricher._compare_numbers(None, "less_or_equal", 20, treat_blank_as_zero=False) is False
    assert enricher._compare_numbers("Hide", "greater_or_equal", 1, treat_blank_as_zero=False) is False
    assert enricher._compare_numbers(None, "less_or_equal", 20, treat_blank_as_zero=True) is True


def test_dates_match_by_calendar_day_not_by_text():
    enricher = DataEnricher(db=None)
    july_first = enricher._parse_calendar_date("7/1/2026")

    assert enricher._parse_calendar_date("9/30/2026") == enricher._parse_calendar_date("09/30/26")
    assert enricher._parse_calendar_date("09/30/26") == enricher._parse_calendar_date("2026-09-30")

    assert enricher._compare_dates("7/2/25", "date_before_or_equal", "7/1/2026") is True
    assert enricher._compare_dates("9/30/26", "date_after_or_equal", "9/30/2026") is True
    assert enricher._compare_dates("9/30/26", "date_between", "7/1/2026", "9/30/2026") is True
    assert enricher._compare_dates("7/1/2026", "date_between", "7/1/2026", "9/30/2026") is True
    assert enricher._compare_dates("10/1/2026", "date_between", july_first, "9/30/2026") is False
    assert enricher._compare_dates("10/1/2026", "date_outside", "7/1/2026", "9/30/2026") is True
    assert enricher._compare_dates("8/1/2026", "date_outside", "7/1/2026", "9/30/2026") is False
    # A blank date does not match a date rule.
    assert enricher._compare_dates(None, "date_before_or_equal", "7/1/2026") is False


def test_outside_date_can_set_text_or_leave_blank():
    enricher = DataEnricher(db=None)
    enricher.supplier_rules = [FakeRule({
        "condition": {
            "type": "condition",
            "field": "confirmed_occupancy",
            "operator": "date_outside",
            "value": "7/1/2026",
            "value_to": "9/30/2026",
            "comparison_type": "date",
        },
        "then_actions": [{
            "type": "set_value",
            "field": "Outside Date Range",
            "value": "Review",
            "output_type": "text",
            "else_enabled": True,
            "else_value": "",
            "else_output_type": "blank",
        }],
    })]

    frame = pd.DataFrame({
        "confirmed_occupancy": ["6/1/2026", "8/15/2026", "10/2/2026"],
    })
    result = enricher.apply_flexible_rules(frame)

    assert result["Outside Date Range"].tolist() == ["Review", "", "Review"]
