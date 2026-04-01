from sheet_key_store import DEFAULT_USER_ID, fetch_key

result, key, message = fetch_key(
    file_name="file2.txt",
    user_id=DEFAULT_USER_ID,
)

print("Result:", result)
print("Message:", message)

if result == "success":
    print("Key found:", key)
else:
    print("Error:", message)
