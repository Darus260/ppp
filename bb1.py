import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

# --- KONFIGURASI ---
FILE_INPUT = "NWSHP_codes_265277_299999.txt"
FILE_OUTPUT = "voucher_valid_final.txt"
BASE_URL = "https://myskill.id/payment/review-cv-ai/695b6ba96qgWXGrJQigK?coupon="

# MODE_HEADLESS = False untuk pertama kali agar bisa login
MODE_HEADLESS = False  

def setup_driver():
    firefox_options = Options()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(current_dir, "profil_bot_myskill_ff")
    
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
        
    firefox_options.add_argument("-profile")
    firefox_options.add_argument(profile_path)

    if MODE_HEADLESS:
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")

    service = Service(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=firefox_options)

def check_vouchers_background():
    try:
        with open(FILE_INPUT, "r") as f:
            codes = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"File {FILE_INPUT} tidak ditemukan!")
        return

    print("Menyiapkan browser Firefox...")
    driver = setup_driver()
    valid_count = 0

    try:
        # --- JEDA UNTUK LOGIN (HANYA JIKA MODE GUI AKTIF) ---
        if not MODE_HEADLESS:
            print("\n[!] MODE TAMPILAN (GUI) AKTIF")
            print("Membuka halaman utama MySkill untuk login...")
            # Buka halaman utama atau halaman login MySkill
            driver.get("https://myskill.id/") 
            
            print("\n" + "="*50)
            print(">>> SILAKAN LOGIN MANUAL DI BROWSER FIREFOX <<<")
            print("Jika sudah berhasil login, kembali ke terminal/CMD ini")
            input("dan tekan tombol [ENTER] untuk mulai mengecek kode...")
            print("="*50 + "\n")
            print("Melanjutkan pengecekan kode otomatis...\n")
        elif MODE_HEADLESS:
            print("Status: Berjalan di Latar Belakang (Headless Mode) 👻\n")

        # --- MULAI LOOPING PENGECEKAN KODE ---
        print(f"Memulai pengecekan {len(codes)} kode...")
        for index, code in enumerate(codes, start=1):
            url = f"{BASE_URL}{code}"
            driver.get(url)
            
            try:
                xpath_selector = "//div[@class='css-te1a66']"
                WebDriverWait(driver, 6).until(
                    EC.presence_of_element_located((By.XPATH, xpath_selector))
                )
                
                print(f"[{index}/{len(codes)}] {code} -> [✔] VALID")
                with open(FILE_OUTPUT, "a") as f_out:
                    f_out.write(f"{code}\n")
                valid_count += 1
                
            except Exception:
                print(f"[{index}/{len(codes)}] {code} -> [X] TIDAK VALID")
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSkrip dihentikan paksa.")
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
