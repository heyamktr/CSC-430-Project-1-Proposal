from sheet_key_store import DEFAULT_USER_ID, store_key

stored, key, message = store_key(
    file_name="file2.txt",
    user_id=DEFAULT_USER_ID,
)

print("Generated key:", key)
print("Stored:", stored)
print("Message:", message)
