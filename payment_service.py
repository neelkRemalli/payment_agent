"""Basic consistency checks for extracted payment details."""

from dataclasses import dataclass
from decimal import Decimal

from extraction_service import PaymentDetails


@dataclass(frozen=True)
class PaymentCheckResult:
    valid: bool
    message: str


def validate_payment(details: PaymentDetails, expected_amount: Decimal | None = None) -> PaymentCheckResult:
    """Check that extracted details contain a positive amount and match any expected amount."""
    if details.amount is None or details.amount <= 0:
        return PaymentCheckResult(False, "A positive payment amount could not be confirmed.")
    if expected_amount is not None and details.amount != Decimal(expected_amount):
        return PaymentCheckResult(False, "Payment amount does not match the expected amount.")
    return PaymentCheckResult(True, "Payment amount confirmed.")
