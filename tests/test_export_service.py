import csv
import json
from decimal import Decimal

from extraction_service import PaymentDetails
from export_service import export_csv, export_json


def test_exports_json(tmp_path):
    path = export_json(PaymentDetails(Decimal("12.30"), "USD", "2025-01-01", "R1"), tmp_path / "payment.json")
    assert json.loads(path.read_text()) == {
        "amount": "12.30", "currency": "USD", "date": "2025-01-01", "reference": "R1"
    }


def test_exports_csv(tmp_path):
    path = export_csv(PaymentDetails(Decimal("12.30"), "USD", None, None), tmp_path / "payment.csv")
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert rows == [{"amount": "12.30", "currency": "USD", "date": "", "reference": ""}]
