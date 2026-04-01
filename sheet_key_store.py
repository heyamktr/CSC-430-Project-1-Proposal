from datetime import date

import requests
from cryptography.fernet import Fernet

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxIfogM5dbClbpDSyYL5rhMVuxeK1gBv-h4qHzlk5p8IN0lMULbmlUUJWOlgONzBbkOzw/exec"
DEFAULT_USER_ID = "u456"
REQUEST_TIMEOUT = 10


def generate_key():
    return Fernet.generate_key().decode()


def fetch_key(file_name, user_id=DEFAULT_USER_ID):
    params = {
        "user_id": user_id,
        "file_name": file_name,
    }

    try:
        response = requests.get(WEB_APP_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return "error", None, f"Could not reach key server: {exc}"
    except ValueError:
        return "error", None, "Key server returned invalid JSON."

    if data.get("status") == "success" and data.get("key"):
        return "success", data["key"], f"Retrieved key for {file_name}."

    message = data.get("message", f"Key not found for {file_name}.")
    return "not_found", None, message


def store_key(
    file_name,
    user_id=DEFAULT_USER_ID,
    key=None,
    status="encrypted",
    progress=0,
    timestamp=None,
):
    key = key or generate_key()
    payload = {
        "user_id": user_id,
        "file_name": file_name,
        "key": key,
        "status": status,
        "progress": progress,
        "timestamp": timestamp or date.today().isoformat(),
    }

    try:
        response = requests.post(WEB_APP_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        return False, key, f"Could not store key for {file_name}: {exc}"

    return True, key, f"Stored key for {file_name}."


def ensure_key(file_name, user_id=DEFAULT_USER_ID):
    result, key, message = fetch_key(file_name, user_id=user_id)
    if result == "success":
        return True, key, message

    if result == "error":
        return False, None, message

    stored, key, message = store_key(file_name, user_id=user_id)
    if stored:
        return True, key, f"Created key for {file_name}."

    return False, None, message
