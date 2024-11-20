import os
import platform
import requests
from time import sleep

# Konfigurasi
VERSION = "v1.0"
APP_TITLE = f"DANA Utility {VERSION}"
DANA_URL = "https://api.dana.id"

# Utilities
def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

def send_request(url, payload=None, token=None, method="GET"):
    headers = {
        "Accept": "application/json",
        "User-Agent": "DANA/1.0.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if method == "POST":
        response = requests.post(url, json=payload, headers=headers)
    else:
        response = requests.get(url, headers=headers)

    try:
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

def save_token(refresh_token, access_token):
    with open("dana_tokens.txt", "w") as f:
        f.write(f"REFRESH_TOKEN={refresh_token}\nACCESS_TOKEN={access_token}")
    print("Token berhasil disimpan!")

def load_token():
    try:
        with open("dana_tokens.txt", "r") as f:
            lines = f.readlines()
            refresh_token = lines[0].split("=")[1].strip()
            access_token = lines[1].split("=")[1].strip()
        return refresh_token, access_token
    except FileNotFoundError:
        print("Token tidak ditemukan. Silakan login terlebih dahulu.")
        return None, None

# Login
def login():
    clear_screen()
    print(f"{APP_TITLE}\n{'#' * 30}\n")
    phone = input("Masukkan nomor telepon (62xxx): ")
    payload = {"phone": phone}

    # Kirim OTP
    response = send_request(f"{DANA_URL}/v1/login", payload, method="POST")
    if not response.get("success"):
        print(f"Error: {response.get('message')}")
        return

    otp_token = response["data"]["otp_token"]
    otp = input("Masukkan OTP: ")

    # Verifikasi OTP
    payload = {"otp": otp, "otp_token": otp_token}
    response = send_request(f"{DANA_URL}/v1/verify-otp", payload, method="POST")
    if not response.get("success"):
        print(f"Error: {response.get('message')}")
        return

    tokens = response["data"]
    save_token(tokens["refresh_token"], tokens["access_token"])
    print("Login berhasil!")

# Cek Saldo
def cek_saldo():
    refresh_token, access_token = load_token()
    if not access_token:
        return

    response = send_request(f"{DANA_URL}/v1/check-balance", token=access_token)
    if not response.get("success"):
        print(f"Error: {response.get('message')}")
        return

    saldo = response["data"]["balance"]
    print(f"Saldo DANA Anda: Rp {saldo:,}")

# Cek Voucher
def cek_voucher():
    refresh_token, access_token = load_token()
    if not access_token:
        return

    response = send_request(f"{DANA_URL}/v1/vouchers", token=access_token)
    if not response.get("success"):
        print(f"Error: {response.get('message')}")
        return

    vouchers = response["data"]["vouchers"]
    if not vouchers:
        print("Tidak ada voucher tersedia.")
    else:
        print("Voucher tersedia:")
        for voucher in vouchers:
            print(f"- {voucher['title']} (Expiry: {voucher['expiry_date']})")

# Menu Utama
def main():
    while True:
        clear_screen()
        print(f"{APP_TITLE}\n{'#' * 30}\n")
        print("1. Login")
        print("2. Cek Saldo")
        print("3. Cek Voucher")
        print("4. Keluar")
        choice = input("Pilih menu: ")

        if choice == "1":
            login()
        elif choice == "2":
            cek_saldo()
        elif choice == "3":
            cek_voucher()
        elif choice == "4":
            print("Keluar dari aplikasi. Terima kasih!")
            break
        else:
            print("Pilihan tidak valid!")
        input("\nTekan Enter untuk kembali ke menu utama...")

if __name__ == "__main__":
    main()
