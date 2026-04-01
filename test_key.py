import requests

url = "https://script.google.com/macros/s/AKfycbxIfogM5dbClbpDSyYL5rhMVuxeK1gBv-h4qHzlk5p8IN0lMULbmlUUJWOlgONzBbkOzw/exec"

params = {
    "user_id": "u456",
    "file_name": "file2.txt"
}

response = requests.get(url, params=params)

print("Status code:", response.status_code)
print("Response text:", response.text)

data = response.json()

if data["status"] == "success":
    key = data["key"]
    print("Key found:", key)
else:
    print("Error:", data["message"])