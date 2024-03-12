import re


def is_email_valid(email: str) -> bool:
    """
    Check if an email is valid.
    """
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    return False
