import re
from datetime import datetime

# Phone length per country - this is the configurable part.
PHONE_DIGITS = {"IN": 10, "SG": 8, "US": 10, "UK": 10, "AE": 9}

# Date formats we accept.
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d %b %Y"]

PAYMENT_MODES = [
    "UPI",
    "CARD",
    "CREDIT CARD",
    "DEBIT CARD",
    "COD",
    "NETBANKING",
    "WALLET",
    "PAYPAL",
]

# Columns that must have a value.
REQUIRED = [
    "order_id",
    "order_date",
    "customer_name",
    "country",
    "phone",
    "product_id",
    "product_name",
    "amount",
    "payment_mode",
]


def check_phone(phone, country):
    expected = PHONE_DIGITS.get(str(country).strip().upper())
    if expected is None:
        return f"unknown country '{country}'"
    digits = re.sub(r"\D", "", str(phone))  # keep only the digits
    if len(digits) != expected:
        return f"{country} phone should be {expected} digits"
    return None


def check_date(value):
    text = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            datetime.strptime(text, fmt)
            return None
        except ValueError:
            continue
    return "invalid date format"


def check_amount(value):
    try:
        if float(value) < 0:
            return "amount cannot be negative"
    except ValueError:
        return "amount is not a number"
    return None


def find_problems(row):
    """Return a list of problems for one row (empty list = row is fine)."""
    problems = []

    for col in REQUIRED:
        if not str(row.get(col, "")).strip():
            problems.append(f"{col} is missing")

    if str(row.get("phone", "")).strip() and str(row.get("country", "")).strip():
        msg = check_phone(row["phone"], row["country"])
        if msg:
            problems.append(msg)

    if str(row.get("order_date", "")).strip():
        msg = check_date(row["order_date"])
        if msg:
            problems.append(msg)

    if str(row.get("amount", "")).strip():
        msg = check_amount(row["amount"])
        if msg:
            problems.append(msg)

    mode = str(row.get("payment_mode", "")).strip().upper()
    if mode and mode not in PAYMENT_MODES:
        problems.append(f"invalid payment mode '{row.get('payment_mode')}'")

    return problems


def validate_dataframe(df):
    errors = []
    valid_index = []
    seen_ids = set()

    for i, row in df.iterrows():
        problems = find_problems(row)

        order_id = str(row.get("order_id", "")).strip()
        if order_id and order_id in seen_ids:
            problems.append("duplicate order_id")
        seen_ids.add(order_id)

        if problems:
            errors.append(
                {
                    "row": int(i) + 2,  # +2 so it matches the line in the CSV
                    "order_id": order_id,
                    "problem": "; ".join(problems),
                }
            )
        else:
            valid_index.append(i)

    cleaned = df.loc[valid_index]
    summary = {
        "total": len(df),
        "valid": len(valid_index),
        "invalid": len(df) - len(valid_index),
    }
    return cleaned, errors, summary
