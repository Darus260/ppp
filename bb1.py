import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

# --- KONFIGURASI ---
FILE_INPUT = "NWSHP_codes_265277_299999.txt"  
FILE_OUTPUT = "voucher_valid_final.txt"
BASE_URL = "#"

# TENTUKAN MODE DI SINI:
# False = Buka browser (Untuk login pertama kali atau melihat prosesnya)
# True  = Tanpa browser / Latar belakang (Agar lebih ringan di RDP)
MODE_HEADLESS = False  

def setup_driver():
    firefox_options = Options()
    
    # Membuat folder khusus untuk profil Firefox agar sesi login tersimpan
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
            # Membaca file dan menghapus baris kosong
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
                # Jeda 4 detik agar React JS di MySkill selesai merender elemen error
                time.sleep(4)
                
                # Membaca HTML mentah dari halaman web
                page_html = driver.page_source.lower()
                
                # Cek kata kunci error langsung dari dalam kode HTML
                if "kupon tidak ditemukan" in page_html or "kupon tidak valid" in page_html or "tidak dapat digunakan" in page_html:
                    print(f"[{index}/{len(codes)}] {code} -> [X] HANGUS / TIDAK DITEMUKAN")
                else:
                    # Jika teks error tidak ada di HTML, berarti kode berhasil dipakai
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
