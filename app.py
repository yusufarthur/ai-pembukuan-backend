from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
import bcrypt
import json
import os
from google.auth import default

app = Flask(__name__)
CORS(app)  # Mengizinkan frontend mengakses backend

# 🔹 Autentikasi Google Sheets
service_account_info = json.loads(os.getenv("SERVICE_ACCOUNT_JSON"))
gc = gspread.service_account_from_dict(service_account_info)

# 🔹 Buka Spreadsheet
spreadsheet = gc.open("User_Login")
sheet = spreadsheet.worksheet("Akun")

# 📌 Hash Password
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password.encode(), salt)
    return hashed_pw.decode()

# 📌 Cek Password
def check_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode(), stored_password.encode())

# 📌 API Registrasi
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data["email"]
    password = data["password"]

    # Cek apakah email sudah ada
    existing_users = sheet.col_values(1)
    if email in existing_users:
        return jsonify({"message": "❌ Email sudah terdaftar!"}), 400

    # Hash password dan simpan ke spreadsheet
    hashed_pw = hash_password(password)
    sheet.append_row([email, hashed_pw])

    return jsonify({"message": "✅ Akun berhasil dibuat!"})

# 📌 API Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    users = sheet.get_all_values()
    for row in users:
        if row[0] == email:
            stored_password = row[1]
            if check_password(stored_password, password):
                return jsonify({"message": f"✅ Login berhasil! Selamat datang, {email}"})
            else:
                return jsonify({"message": "❌ Password salah!"}), 400

    return jsonify({"message": "❌ Email tidak ditemukan!"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
