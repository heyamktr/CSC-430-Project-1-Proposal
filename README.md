# 🔐 Key Storage System (Google Sheets + Apps Script + Python)

This module handles storing and retrieving encryption keys using:
- Google Sheets (database)
- Google Apps Script (API)
- Python (client)

---

## 📊 Google Sheet

Link: [PASTE YOUR GOOGLE SHEET LINK HERE]

Required columns (do not change order):

user_id | file_name | key | status | progress | timestamp

---

## 🌐 Web App URL

Replace in both Python files:

YOUR_WEB_APP_URL

---

## ⚙️ Setup (Do this once)

1. Open Google Sheet → Extensions → Apps Script  
2. Make sure both `doGet` and `doPost` exist  
3. Deploy as Web App:
   - Execute as: Me
   - Access: Anyone  
4. Copy the Web App URL  

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