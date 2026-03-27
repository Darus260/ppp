import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- KONFIGURASI ---
FILE_INPUT = "NWSHP_codes_265277_299999.txt"  
FILE_OUTPUT = "voucher_valid_final.txt"
BASE_URL = "#"

# TENTUKAN MODE DI SINI:
# False = Buka browser (Untuk login pertama kali)
# True  = Tanpa browser / Latar belakang
MODE_HEADLESS = False  

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")
    
    # --- AMUNISI ANTI-CRASH CHROME DI RDP/SERVER ---
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--remote-debugging-port=9222")
    # -----------------------------------------------
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(current_dir, "profil_bot_myskill_chrome")
    chrome_options.add_argument(f"user-data-dir={profile_path}")

    if MODE_HEADLESS:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def check_vouchers_background():
    try:
        with open(FILE_INPUT, "r") as f:
            codes = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"File {FILE_INPUT} tidak ditemukan!")
        return

    print("Menyiapkan browser Chrome...")
    driver = setup_driver()
    valid_count = 0

    try:
        if not MODE_HEADLESS:
            print("\n[!] MODE TAMPILAN (GUI) AKTIF")
            print("Membuka halaman utama MySkill untuk login...")
            driver.get("https://myskill.id/") 
            
            print("\n" + "="*50)
            print(">>> SILAKAN LOGIN MANUAL DI BROWSER CHROME <<<")
            print("Jika sudah berhasil login, kembali ke terminal/CMD ini")
            input("dan tekan tombol [ENTER] untuk mulai mengecek kode...")
            print("="*50 + "\n")
            print("Melanjutkan pengecekan kode otomatis...\n")
        elif MODE_HEADLESS:
            print("Status: Berjalan di Latar Belakang (Headless Mode) 👻\n")

        print(f"Memulai pengecekan {len(codes)} kode...")

        for index, code in enumerate(codes, start=1):
            url = f"{BASE_URL}{code}"
            driver.get(url)
            
            try:
                # Jeda 3 detik agar pesan error "Kupon tidak ditemukan" sempat muncul
                time.sleep(3)
                
                # Baca semua teks yang ada di layar
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                
                # Cek apakah ada tulisan error
                if "kupon tidak ditemukan" in page_text or "kupon tidak valid" in page_text:
                    print(f"[{index}/{len(codes)}] {code} -> [X] HANGUS / TIDAK DITEMUKAN")
                else:
                    print(f"[{index}/{len(codes)}] {code} -> [✔] VALID & BISA DIPAKAI")
                    with open(FILE_OUTPUT, "a") as f_out:
                        f_out.write(f"{code}\n")
                    valid_count += 1
                
            except Exception as e:
                print(f"[{index}/{len(codes)}] {code} -> [?] ERROR MENGECEK HALAMAN")
            
    except KeyboardInterrupt:
        print("\nSkrip dihentikan paksa oleh pengguna.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        driver.quit()
        print("\n" + "="*40)
        print("PENGECEKAN SELESAI!")
        print(f"Total Voucher Valid: {valid_count}")
        print("="*40)

if __name__ == "__main__":
    check_vouchers_background()
