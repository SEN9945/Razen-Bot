<p align="center">
  <img src="https://media1.tenor.com/m/DxQuY4U_Wf0AAAAC/rei-codebreaker.gif" alt="Razen Bot AI Assistant in Telegram" width="700"/>
</p>

<h1 align="center">Razen - Asisten Pribadi Cerdas Bertenaga AI</h1>

<p align="center">
    <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python" alt="Python Version"></a>
    <a href="#"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <strong>Razen</strong> adalah sebuah bot asisten pribadi Telegram yang cerdas, dirancang untuk menjadi jembatan antara percakapan sehari-hari Anda dengan ekosistem produktivitas Google Workspace. Ditenagai oleh <strong>Google Gemini AI</strong>, Razen mampu memahami perintah dalam bahasa natural dan mengeksekusi berbagai tugas secara efisien.
</p>

---

## ✨ Fitur Unggulan

| Ikon | Fitur                  | Deskripsi Singkat                                                                                             |
| :--: | ---------------------- | ------------------------------------------------------------------------------------------------------------- |
|  🧠  | **Otak AI Cerdas** | Memahami bahasa natural menggunakan `gemini-1.5-flash` untuk interaksi yang lebih intuitif.                   |
|  🔒  | **Keamanan Maksimal** | Akses bot sepenuhnya terbatas pada User ID yang telah diotorisasi, menjamin privasi data Anda.                 |
|  🗂️  | **Manajemen Drive** | Upload file secara terorganisir, cari file/folder, dan tampilkan daftar file berdasarkan tipe.                |
|  ✍️  | **Manajemen Docs** | Buat, tambah, dan baca catatan Google Docs langsung dari Telegram.                                            |
|  📊  | **Manajemen Sheets** | Catat pengeluaran, baca isi sheet, dan hitung total kolom secara otomatis.                                    |

---

## 📁 Struktur Proyek

Agar bot dapat berjalan, repositori Anda harus memiliki struktur file berikut. Anda hanya perlu menyediakan file yang ditandai `(Buat Sendiri)`.

```
/MyRazenBot
├── .venv/                     # (Dibuat otomatis oleh Python)
├── razen_bot.py               # File utama bot yang Anda miliki
├── authenticate_google.py     # (Buat Sendiri) Skrip untuk otentikasi pertama kali
├── requirements.txt           # (Buat Sendiri) Daftar pustaka (library) yang dibutuhkan
├── .env                       # (Buat Sendiri) File untuk menyimpan semua kunci rahasia
├── credentials.json           # (Unduh dari Google) Kunci akses ke Google Cloud
└── token.json                 # (Dihasilkan otomatis) Token izin Google Anda
```

---

## 🚀 Panduan Instalasi Lengkap

Ikuti langkah-langkah di bawah ini secara berurutan untuk menjalankan Razen dari awal.

### Langkah 1: Persiapan Awal

1.  **Kloning Repositori Anda** di dalam folder bot milik anda
     ```bash
    cd NAMA_REPO_ANDA
    ```
    ```bash
    git clone https://github.com/SEN9945/Razen-Bot.git
    ```

3.  **Buat Virtual Environment**
    > **Penting:** Langkah ini sangat direkomendasikan untuk mengisolasi "perkakas" proyek Anda dan mencegah konflik.
    ```bash
    # Untuk Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # Untuk macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

### Langkah 2: Membuat File yang Diperlukan

Anda perlu membuat 3 file baru secara manual di dalam folder proyek Anda.

1.  **Buat `requirements.txt`**
    File ini berisi daftar semua "perkakas" Python yang dibutuhkan Razen.
    ```text
    python-telegram-bot
    python-dotenv
    google-api-python-client
    google-auth-httplib2
    google-auth-oauthlib
    gspread
    google-generativeai
    ```

2.  **Buat `authenticate_google.py`**
    File ini adalah skrip khusus yang hanya akan kita jalankan sekali untuk mendapatkan izin dari Google.
    ```python
    import os.path
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    # SCOPES ini harus sama persis dengan yang ada di razen_bot.py
    SCOPES = [
        "[https://www.googleapis.com/auth/drive](https://www.googleapis.com/auth/drive)",
        "[https://www.googleapis.com/auth/documents](https://www.googleapis.com/auth/documents)",
        "[https://www.googleapis.com/auth/spreadsheets](https://www.googleapis.com/auth/spreadsheets)"
    ]

    def main():
        creds = None
        if os.path.exists("token.json"):
            print("File token.json sudah ada. Hapus file tersebut jika Anda ingin melakukan otentikasi ulang.")
            return

        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())
        
        print("\nOtentikasi berhasil! File 'token.json' telah dibuat.")
        print("Anda sekarang bisa menjalankan bot utama: python razen_bot.py")

    if __name__ == "__main__":
        main()
    ```

3.  **Buat `.env`**
    Ini adalah "brankas" tempat kita menyimpan semua kunci rahasia.
    ```env
    TELEGRAM_TOKEN="TOKEN_TELEGRAM_ANDA"
    ADMIN_USER_ID="USER_ID_TELEGRAM_ANDA"
    GEMINI_API_KEY="KUNCI_API_GEMINI_ANDA"
    YOUR_GOOGLE_EMAIL="emailanda@gmail.com" //Opsional
    ```

### Langkah 3: Mengisi Kunci Rahasia & Kredensial

Sekarang, mari kita isi "brankas" kita.

1.  **`TELEGRAM_TOKEN`**: Dapatkan dari [**@BotFather**](https://t.me/BotFather) di Telegram dengan membuat bot baru.
2.  **`ADMIN_USER_ID`**: Dapatkan User ID Telegram Anda dari [**@userinfobot**](https://t.me/userinfobot).
3.  **`GEMINI_API_KEY`**: Dapatkan dari [**Google AI Studio**](https://aistudio.google.com/app/apikey).
4.  **`YOUR_GOOGLE_EMAIL`**: Isi dengan alamat email Google Anda (Opsional untuk fitur Sheets).
5.  **`credentials.json`**:
    * Buat proyek di [**Google Cloud Console**](https://console.cloud.google.com/).
    * Aktifkan API: **Google Drive API**, **Google Docs API**, dan **Google Sheets API**.
    * Konfigurasi "OAuth consent screen" (pilih "External" dan tambahkan email Anda sebagai "Test user").
    * Buat kredensial baru dengan tipe "OAuth client ID" dan pilih "Desktop app".
    * Unduh file JSON yang dihasilkan, **ganti namanya menjadi `credentials.json`**, dan letakkan di folder utama proyek.

### Langkah 4: Instalasi & Otentikasi Final

1.  **Instal Semua Pustaka (Library)**
    Kembali ke terminal Anda (pastikan virtual environment aktif) dan jalankan:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Jalankan Otentikasi Google**
    Ini adalah langkah satu kali untuk menghasilkan `token.json`.
    ```bash
    python authenticate_google.py
    ```
    Sebuah tab browser akan terbuka. Ikuti proses login dan berikan semua izin yang diminta.

### Langkah 5: Jalankan Bot!

Setelah file `token.json` muncul, Anda siap untuk menjalankan Razen.
```bash
python razen_bot.py
```
Bot Anda sekarang sudah aktif! Buka Telegram dan mulailah berinteraksi dengannya.

---

## 🤖 Contoh Penggunaan

Berikut adalah beberapa contoh cara berinteraksi dengan Razen.
Buka Bot Telegram anda dan kirim perintah `/start` untuk melihat daftar lengkap kemampuannya.


| Perintah Spesifik (Manual)                                         | Percakapan Natural (AI)                                       |
| ------------------------------------------------------------------ | ------------------------------------------------------------- |
| `/cari Laporan Keuangan`                                           | "Razen, tolong carikan aku presentasi proyek alfa"            |
| `/list dokumen`                                                    | "tampilkan semua file pdf saya"                               |
| `/catat Rapat Penting \| Hasil rapat adalah...`                    | "catat ide baru dengan isi: coba integrasi Google Calendar"   |
| `/tambahcatatan Rapat Penting \| Tambahan: ...`                    | "tambahkan ke daftar belanja: beli buah-buahan"               |
| `/bacacatatan Rapat Penting`                                       | "apa isi dari catatan rapat kemarin?"                         |
| `/lapor Makanan 50000`                                             | "baru saja keluar uang 35000 untuk bensin"                    |
| `/bacasheet Laporan Keuangan Razen \| Juli 2025`                   | "baca laporan keuangan bulan lalu"                            |
| `/hitung Laporan Keuangan Razen \| Juli 2025 \| Jumlah`            | "berapa total pengeluaran untuk makanan bulan ini?"           |
| `/listsheets`                                                      | "tampilkan semua sheet yang saya punya"                       |

---

## 📜 Lisensi

Proyek ini didistribusikan di bawah Lisensi MIT.
