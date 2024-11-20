from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
import subprocess
import sys
import requests

# Fungsi untuk memeriksa dan menginstal dependensi
def install_dependencies():
    required_packages = ["requests", "rich"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Pustaka '{package}' tidak ditemukan. Menginstal...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Panggil fungsi untuk memastikan dependensi terinstal
install_dependencies()

# Inisialisasi console Rich
console = Console()

# Konfigurasi API
BASE_URL = "https://dashboard.dana.id/app/"
ENDPOINTS = {
    "request_otp": "/request-otp",
    "verify_otp": "/verify-otp",
    "balance": "/balance",
    "vouchers": "/vouchers",
}

# Fungsi untuk mengonversi nomor telepon ke format internasional
def format_phone_number(phone_number):
    if phone_number.startswith("0"):
        return "+62" + phone_number[1:]
    elif phone_number.startswith("+62"):
        return phone_number
    else:
        raise ValueError("[red]Nomor telepon harus diawali dengan '0' atau '+62'.[/red]")

# Fungsi untuk meminta kode OTP
def request_otp(phone_number):
    formatted_phone = format_phone_number(phone_number)
    console.print(f"\n[blue]Mengirim kode OTP ke {formatted_phone}...[/blue]")
    
    url = BASE_URL + ENDPOINTS["request_otp"]
    payload = {"phone_number": formatted_phone}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "success":
            console.print("[green]Kode OTP berhasil dikirim![/green]")
            return True
        else:
            console.print(f"[red]Error: {data.get('message', 'Gagal mengirim kode OTP.')}[/red]")
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Kesalahan jaringan: {e}[/red]")
    return False

# Fungsi untuk verifikasi kode OTP
def verify_otp(phone_number, otp_code):
    formatted_phone = format_phone_number(phone_number)
    console.print("\n[blue]Memverifikasi kode OTP...[/blue]")
    
    url = BASE_URL + ENDPOINTS["verify_otp"]
    payload = {"phone_number": formatted_phone, "otp_code": otp_code}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        token = data.get("token")
        if token:
            console.print("[green]Login berhasil![/green]")
            return token
        else:
            console.print(f"[red]Error: {data.get('message', 'Gagal verifikasi OTP.')}[/red]")
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Kesalahan jaringan: {e}[/red]")
    return None

# Fungsi untuk melihat saldo
def check_balance(token):
    console.print("\n[blue]Mengambil saldo...[/blue]")
    
    url = BASE_URL + ENDPOINTS["balance"]
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        balance = data.get("balance")
        if balance is not None:
            console.print(f"[green]Saldo Anda: Rp{balance:,}[/green]")
        else:
            console.print("[red]Gagal mendapatkan saldo.[/red]")
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Kesalahan jaringan: {e}[/red]")

# Fungsi untuk melihat voucher
def check_vouchers(token):
    console.print("\n[blue]Mengambil daftar voucher...[/blue]")
    
    url = BASE_URL + ENDPOINTS["vouchers"]
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        vouchers = data.get("vouchers", [])
        
        if vouchers:
            table = Table(title="Voucher Anda")
            table.add_column("No", style="cyan", justify="center")
            table.add_column("Nama Voucher", style="magenta")
            table.add_column("Diskon", style="green", justify="center")
            
            for idx, voucher in enumerate(vouchers, start=1):
                name = voucher.get("name", "Nama tidak tersedia")
                discount = voucher.get("discount", "Diskon tidak tersedia")
                table.add_row(str(idx), name, discount)
            
            console.print(table)
        else:
            console.print("[yellow]Anda tidak memiliki voucher.[/yellow]")
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Kesalahan jaringan: {e}[/red]")

# Fungsi untuk menampilkan menu
def main_menu():
    console.print(Panel.fit(
        "[bold magenta]Selamat Datang di DANA by Becode[/bold magenta]\n\n[cyan]Aplikasi ini dibuat untuk tujuan pembelajaran tanpa profit.[/cyan]",
        title="Aplikasi DANA",
        subtitle="v1.0",
    ))
    phone_number = Prompt.ask("[cyan]Masukkan nomor telepon Anda[/cyan]")
    
    try:
        if request_otp(phone_number):
            otp_code = Prompt.ask("[cyan]Masukkan kode OTP yang diterima[/cyan]")
            token = verify_otp(phone_number, otp_code)
            if token:
                while True:
                    console.print("\n[bold blue]Menu Utama:[/bold blue]")
                    console.print("1. [green]Cek Saldo[/green]")
                    console.print("2. [green]Cek Voucher[/green]")
                    console.print("3. [red]Keluar[/red]")
                    
                    choice = Prompt.ask("[cyan]Pilih menu (1/2/3)[/cyan]")
                    
                    if choice == "1":
                        check_balance(token)
                    elif choice == "2":
                        check_vouchers(token)
                    elif choice == "3":
                        console.print("[bold red]Terima kasih telah menggunakan DANA by Becode. Sampai jumpa![/bold red]")
                        break
                    else:
                        console.print("[red]Pilihan tidak valid. Silakan pilih kembali.[/red]")
    except ValueError as e:
        console.print(f"[red]Kesalahan: {e}[/red]")

# Eksekusi
if __name__ == "__main__":
    main_menu()
