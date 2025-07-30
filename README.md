# Razen Bot - Asisten Pribadi Cerdas untuk Google Workspace

**Razen Bot** adalah sebuah asisten pribadi yang sangat cerdas dan aman, dirancang untuk menjadi jembatan antara antarmuka percakapan Telegram yang nyaman dengan ekosistem Google Workspace Anda (Drive, Docs, Sheets). Dibangun dengan filosofi *keamanan di atas segalanya*, Razen memungkinkan Anda mengelola file, catatan, dan laporan keuangan hanya dengan menggunakan bahasa natural.

---

## 🌟 Fitur Unggulan

*   **Otak AI Cerdas (Google Gemini):** Memahami perintah bahasa alami. Anda tidak perlu menghafal perintah-perintah kaku.
*   **Manajemen Google Drive Lengkap:**
    *   Upload file, foto, dan video dengan alur kerja otomatis atau manual.
    *   Pencarian file dan folder interaktif.
    *   Melihat daftar file berdasarkan tipe (dokumen, gambar, video, dll.) dengan sistem halaman (paginasi).
*   **Sekretaris Pribadi (Google Docs):**
    *   Membuat, menambah, dan membaca catatan langsung dari Telegram.
*   **Akuntan Pribadi (Google Sheets):**
    *   Mencatat laporan pengeluaran dengan mudah.
    *   Membaca isi spreadsheet.
    *   Menghitung total dari kolom tertentu secara otomatis.
*   **Keamanan Terjamin:** Akses terbatas hanya untuk Admin dan otentikasi aman menggunakan OAuth 2.0.

---

## 🚀 Panduan Instalasi

Ikuti langkah-langkah berikut untuk menjalankan Razen Bot di server Anda.

### 1. Prasyarat

*   Python 3.10 atau lebih tinggi.
*   Akun Google.
*   Akun Telegram dan bot yang dibuat melalui [BotFather](https://t.me/BotFather).

### 2. Kloning Repositori

```bash
git clone https://github.com/YOUR_USERNAME/MyRazenBot.git
cd MyRazenBot
```

### 3. Setup Virtual Environment

Sangat disarankan untuk menggunakan virtual environment.

```bash
# Buat virtual environment
python -m venv .venv

# Aktifkan (Windows)
.venv\Scripts\activate

# Aktifkan (macOS/Linux)
# source .venv/bin/activate
```

### 4. Instalasi Dependensi

Instal semua pustaka yang diperlukan dengan satu perintah:

```bash
pip install -r requirements.txt
```

### 5. Konfigurasi Google API

1.  Buka [Google Cloud Console](https://console.cloud.google.com/).
2.  Buat proyek baru.
3.  Aktifkan API berikut untuk proyek Anda:
    *   **Google Drive API**
    *   **Google Docs API**
    *   **Google Sheets API**
4.  Buka menu "Credentials" (Kredensial).
5.  Buat "OAuth client ID" baru.
6.  Pilih "Desktop app" sebagai tipe aplikasi.
7.  Setelah dibuat, unduh file JSON kredensial tersebut dan **ganti namanya menjadi `credentials.json`**, lalu letakkan di dalam folder proyek `MyRazenBot`.

### 6. Konfigurasi Environment Bot

1.  Buat file baru bernama `.env` di dalam folder proyek.
2.  Isi file tersebut dengan format berikut:

```
TELEGRAM_TOKEN="TOKEN_BOT_TELEGRAM_ANDA"
ADMIN_USER_ID="USER_ID_TELEGRAM_ANDA"
GEMINI_API_KEY="API_KEY_GEMINI_ANDA"
YOUR_GOOGLE_EMAIL="EMAIL_GOOGLE_ANDA_UNTUK_SHARE_SHEET"
```

*   `TELEGRAM_TOKEN`: Dapatkan dari BotFather.
*   `ADMIN_USER_ID`: Dapatkan dari bot seperti [@userinfobot](https://t.me/userinfobot).
*   `GEMINI_API_KEY`: Dapatkan dari [Google AI Studio](https://aistudio.google.com/app/apikey).
*   `YOUR_GOOGLE_EMAIL`: Opsional, digunakan untuk membagikan akses spreadsheet yang baru dibuat secara otomatis.

### 7. Otentikasi Google (Langkah Krusial)

Jalankan skrip `authenticate_google.py` untuk menghasilkan `token.json` yang akan digunakan bot untuk mengakses akun Google Anda.

```bash
python authenticate_google.py
```

*   Ikuti instruksi di terminal. Anda akan diminta untuk membuka sebuah URL di browser, login dengan akun Google Anda, dan memberikan izin.
*   Salin kode otorisasi yang diberikan dan tempelkan kembali ke terminal.
*   File `token.json` akan dibuat secara otomatis. **Langkah ini hanya perlu dilakukan sekali.**

### 8. Jalankan Bot!

Sekarang Anda siap untuk menjalankan bot utama.

```bash
python razen_bot.py
```

Buka Telegram dan kirim perintah `/start` untuk melihat daftar lengkap kemampuannya.

---

## 💡 Contoh Penggunaan AI

*   `carikan saya file presentasi Q3`
*   `tampilkan semua file pdf saya`
*   `buat catatan rapat penting hari ini isinya adalah...`
*   `tambahkan ke daftar belanja: beli telur dan roti`
*   `apa isi catatan proyek alpha?`
*   `catat pengeluaran transportasi 150000`
*   `baca laporan keuangan bulan lalu`
*   `berapa total pengeluaran untuk makanan bulan ini?`
