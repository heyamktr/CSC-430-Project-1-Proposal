import requests
from cryptography.fernet import Fernet

url = "https://script.google.com/macros/s/AKfycbxIfogM5dbClbpDSyYL5rhMVuxeK1gBv-h4qHzlk5p8IN0lMULbmlUUJWOlgONzBbkOzw/exec"

key = Fernet.generate_key().decode()

payload = {
    "user_id": "u456",
    "file_name": "file2.txt",
    "key": key,
    "status": "encrypted",
    "progress": 0,
    "timestamp": "2026-03-31"
}

response = requests.post(url, json=payload)

print("Generated key:", key)
print("Status code:", response.status_code)
print("Response text:", response.text)