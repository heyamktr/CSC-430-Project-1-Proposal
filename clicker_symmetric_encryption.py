import json
from pathlib import Path

from cryptography.fernet import Fernet

from sheet_key_store import DEFAULT_USER_ID, store_key

BASE_DIR = Path(__file__).resolve().parent
THE_DIRECTORY = BASE_DIR / "clicker_game_encryption"
USER_FILES = THE_DIRECTORY / "user_files"
ENCRYPTED_FILES = THE_DIRECTORY / "encrypted_files"
KEY_FILES = THE_DIRECTORY / "key_files"
RECORD_FILE = THE_DIRECTORY / "record.json"
PLAYER_ID = DEFAULT_USER_ID
GAME_FILE_CONTENTS = {
    "file1.txt": "This is the first file in the clicker game.",
    "file2.txt": "This file belongs to the clicker game shop.",
    "file3.txt": "This is the protected file with the highest cost.",
}


def resolve_user_id(user_id=None):
    return user_id or PLAYER_ID


def ensure_directories():
    THE_DIRECTORY.mkdir(exist_ok=True)
    USER_FILES.mkdir(exist_ok=True)
    ENCRYPTED_FILES.mkdir(exist_ok=True)
    KEY_FILES.mkdir(exist_ok=True)


def create_files():
    ensure_directories()

    for name, content in GAME_FILE_CONTENTS.items():
        path = USER_FILES / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def load_record():
    if not RECORD_FILE.exists():
        return {}

    try:
        record = json.loads(RECORD_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    if isinstance(record, dict):
        return record

    return {}


def save_record(record):
    RECORD_FILE.write_text(json.dumps(record, indent=2), encoding="utf-8")


def create_key_for_file(file_path, overwrite=False):
    key_path = KEY_FILES / f"{file_path.name}.key"
    if key_path.exists() and not overwrite:
        existing_key = key_path.read_text(encoding="utf-8").strip()
        if existing_key:
            return existing_key, key_path

    key_text = Fernet.generate_key().decode()
    key_path.write_text(key_text, encoding="utf-8")
    return key_text, key_path


def encrypt_file(file_path, key_text):
    cipher = Fernet(key_text.encode())
    original_content = file_path.read_bytes()
    encrypted_content = cipher.encrypt(original_content)

    encrypted_file = ENCRYPTED_FILES / f"{file_path.name}.encrypted"
    encrypted_file.write_bytes(encrypted_content)
    return encrypted_file


def decrypt_file(file_name, key_text):
    record = load_record()
    encrypted_path = None

    if file_name in record:
        encrypted_path = Path(record[file_name]["encrypted_copy"])
    else:
        encrypted_path = ENCRYPTED_FILES / f"{file_name}.encrypted"

    if not encrypted_path.exists():
        raise FileNotFoundError(f"Encrypted file not found for {file_name}.")

    cipher = Fernet(key_text.encode())
    decrypted_content = cipher.decrypt(encrypted_path.read_bytes())
    return decrypted_content.decode("utf-8")


def sync_file(file_name, user_id=None, force_upload=False):
    ensure_directories()

    if file_name not in GAME_FILE_CONTENTS:
        raise ValueError(f"Unsupported file name: {file_name}")

    user_id = resolve_user_id(user_id)
    file_path = USER_FILES / file_name
    if not file_path.exists():
        file_path.write_text(GAME_FILE_CONTENTS[file_name], encoding="utf-8")

    key_text, key_path = create_key_for_file(file_path)
    encrypted_file = encrypt_file(file_path, key_text)

    record = load_record()
    previous_entry = record.get(file_name, {})
    should_upload = force_upload or not previous_entry.get("uploaded_to_google_sheet") or previous_entry.get("user_id") != user_id

    if should_upload:
        uploaded, _, upload_message = store_key(
            file_name=file_path.name,
            user_id=user_id,
            key=key_text,
            status="encrypted",
            progress=100,
        )
    else:
        uploaded = True
        upload_message = "Key already synced to Google Sheet."

    record[file_name] = {
        "user_id": user_id,
        "user_file": str(file_path),
        "encrypted_copy": str(encrypted_file),
        "key_file": str(key_path),
        "uploaded_to_google_sheet": uploaded,
        "upload_message": upload_message,
    }
    save_record(record)
    return record[file_name]


def sync_all_files(user_id=None, force_upload=False):
    user_id = resolve_user_id(user_id)
    create_files()

    synced = {}
    for file_name in GAME_FILE_CONTENTS:
        synced[file_name] = sync_file(file_name, user_id=user_id, force_upload=force_upload)

    return synced


def encrypt_files(user_id=None, force_upload=False):
    synced = sync_all_files(user_id=user_id, force_upload=force_upload)

    for file_name, details in synced.items():
        key_path = Path(details["key_file"])
        print(f"{file_name}: encrypted")
        print(f"  key file: {key_path.name}")
        print(f"  sheet upload: {details['upload_message']}")

    return synced


def main():
    encrypt_files()
    print("Finished encrypting files and uploading keys.")


if __name__ == "__main__":
    main()
