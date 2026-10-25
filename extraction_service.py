"""Extract common payment fields from OCR text."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re


@dataclass(frozen=True)
class PaymentDetails:
    amount: Decimal | None = None
    currency: str | None = None
    date: str | None = None
    reference: str | None = None


def extract_payment_details(text: str) -> PaymentDetails:
    """Parse common fields from text obtained from a payment receipt.

    OCR is intentionally kept outside this function so OCR engines can be
    selected or supplied separately.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    amount = None
    currency = None
    match = re.search(r"(?i)(?:\b(USD|EUR|GBP|INR|CAD|AUD)\b\s*)?([$€£₹])?\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)", text)
    if match:
        currency = match.group(1) or {"$": "USD", "€": "EUR", "£": "GBP", "₹": "INR"}.get(match.group(2))
        try:
            amount = Decimal(match.group(3).replace(",", ""))
        except InvalidOperation:
            pass

    date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    ref_match = re.search(r"(?i)\b(?:reference|ref|transaction\s*id)\s*[:#-]?\s*([A-Z0-9-]+)", text)
    return PaymentDetails(
        amount=amount,
        currency=currency,
        date=date_match.group(1) if date_match else None,
        reference=ref_match.group(1) if ref_match else None,
    )
