# 🔐 Key Storage System (Google Sheets + Apps Script + Python)

This module handles storing and retrieving encryption keys using:
- Google Sheets (database)
- Google Apps Script (API)
- Python (client)

---

## 📊 Google Sheet

Link: [(https://docs.google.com/spreadsheets/d/1TTR2chLpBpXfH6aXWID1bqVE6L5BP574UCzlMUK99cU/edit?usp=sharing)]

Required columns (do not change order):

user_id | file_name | key | status | progress | timestamp

---

## 🐍 Install dependencies

Run once:

pip install requests cryptography

---

## ▶️ How to run

### 1. Store a key (simulate encryption)

Run:

python write_key.py

What it does:
- generates a random key
- sends it to Google Sheets
- adds a new row

---

### 2. Retrieve a key (simulate decryption)

Run:

python test_key.py

What it does:
- requests key using user_id + file_name
- returns the stored key from Google Sheets

---

## 🔁 Typical workflow

1. Run `write_key.py` → stores key  
2. Run `test_key.py` → retrieves key  

---

## ⚠️ Important

- user_id and file_name must match exactly between scripts and sheet  
- Do NOT change column order in Google Sheet  
- Always redeploy Apps Script after changes  

---

## 🐞 Common errors

Script function not found: doPost  
→ forgot to redeploy Apps Script  

Key not found  
→ mismatch in user_id or file_name  

Permission error  
→ Web app not set to "Anyone"  

---

## 🔐 Note

This is a **controlled class project simulation**.  
Only use test files.