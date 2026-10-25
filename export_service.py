"""Export extracted payment details as JSON or CSV."""

import csv
import json
from dataclasses import asdict
from pathlib import Path

from extraction_service import PaymentDetails


def export_json(details: PaymentDetails, path: str | Path) -> Path:
    destination = Path(path)
    payload = asdict(details)
    payload["amount"] = str(details.amount) if details.amount is not None else None
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return destination


def export_csv(details: PaymentDetails, path: str | Path) -> Path:
    destination = Path(path)
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("amount", "currency", "date", "reference"))
        writer.writeheader()
        row = asdict(details)
        row["amount"] = str(details.amount) if details.amount is not None else ""
        writer.writerow({key: value if value is not None else "" for key, value in row.items()})
    return destination
