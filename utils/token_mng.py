import os
import json
import time
import logging

TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".token")


def save_token(access_token: str, expires_in: int) -> None:
    """
    Save the access_token and expires_in(the expiration date) to the .token file in the project root.
    """
    data = {
        "access_token": access_token,
        "expires_in": time.time() + expires_in,
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f)


def load_token() -> tuple[str | None, int]:
    """
    Load the access_token and expires_in from the .token file.
    Returns None if the file does not exist or is invalid.
    """
    if not os.path.exists(TOKEN_FILE):
        return None, 0
    try:
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
        if "access_token" in data and "expires_in" in data:
            return data["access_token"], data["expires_in"]
        return None, 0
    except Exception:
        logging.error(f"Failed to load token from {TOKEN_FILE}")
        return None, 0
