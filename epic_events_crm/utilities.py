import re


def is_email_valid(email: str) -> bool:
    """Check if an email is valid."""
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    return False


def remove_spaces_and_hyphens(string: str) -> str:
    """Remove spaces and hyphens from a string."""
    return string.replace(" ", "").replace("-", "")


def is_phone_valid(phone: str) -> bool:
    """Check if a phone number is valid."""
    phone = remove_spaces_and_hyphens(phone)
    min_length = 7
    pattern = r"^(\+[\d]{1,3}[\d]{1,14}|[\d]{1,15})$"  # ITU E.164 standard
    if re.match(pattern, phone) and len(phone) >= min_length:
        return True
    return False
