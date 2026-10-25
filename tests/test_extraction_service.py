from decimal import Decimal

from extraction_service import extract_payment_details


def test_extracts_amount_date_and_reference():
    result = extract_payment_details("Paid USD 1,250.50 on 2025-03-04. Reference: ABC-123")
    assert result.amount == Decimal("1250.50")
    assert result.currency == "USD"
    assert result.date == "2025-03-04"
    assert result.reference == "ABC-123"


def test_missing_fields_are_none():
    assert extract_payment_details("Receipt received").amount is None
