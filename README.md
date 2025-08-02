<p align="center">
  <img src="https://media1.tenor.com/m/DxQuY4U_Wf0AAAAC/rei-codebreaker.gif" alt="Razen Bot AI Assistant in Telegram" width="700"/>
</p>

<h1 align="center">Razen - Asisten Pribadi Cerdas Bertenaga AI</h1>

<p align="center">
    <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python" alt="Python Version"></a>
    <a href="#"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"></a>
    <a href="https://www.youtube.com/@iceskey"><img src="https://img.shields.io/badge/YouTube-iceskey-red?style=for-the-badge&logo=youtube" alt="YouTube"></a>
    <a href="https://git-scm.com/downloads/" target="_blank"><img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git"></a>
    <a href="https://code.visualstudio.com/" target="_blank"><img src="https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white" alt="VS Code"></a>
    <a href="#"><img src="https://img.shields.io/badge/Bahasa-Indonesia-lightgrey?style=for-the-badge&logo=googletranslate" alt="Language"></a>
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

### 📁 Struktur Proyek Akhir

Setelah semua langkah selesai, folder proyek Anda akan terlihat seperti ini:

```
/MyRazenBot/Razen-Bot
├── .venv/                     # (Dibuat otomatis oleh Python)
├── razen_bot.py               # File utama bot yang Anda miliki
├── authenticate_google.py     # (Buat Sendiri) Skrip untuk otentikasi pertama kali
├── requirements.txt           # (Buat Sendiri) Daftar pustaka (library) yang dibutuhkan
├── .env                       # (Buat Sendiri) File untuk menyimpan semua kunci rahasia
├── .gitignore                 # (Buat Sendiri) Mengamankan file rahasia dari Git
├── credentials.json           # (Unduh dari Google) Kunci akses ke Google Cloud
└── token.json                 # (Dihasilkan otomatis) Token izin Google Anda
```

---

## 🚀 Panduan Instalasi Lengkap

Sebelum memulai, pastikan Anda sudah menginstal perangkat lunak berikut:
1.  **[Git](https://git-scm.com/downloads/):** Sistem untuk mengelola versi kode.
2.  **[Python](https://www.python.org/downloads/):** Bahasa pemrograman yang kita gunakan (versi 3.10+).
3.  **[Visual Studio Code](https://code.visualstudio.com/):** Editor kode gratis. Kita akan menggunakannya untuk mengedit file.

Ikuti langkah-langkah di bawah ini secara berurutan untuk menjalankan Razen dari awal.
Panduan ini terbagi menjadi dua bagian utama:
* **Bagian A: Persiapan di Komputer Lokal Anda (yang memiliki Browser)**
* **Bagian B: Pemasangan di Server/VPS/Termux (hanya Terminal)**

#### A1. Dapatkan Semua Kunci Rahasia

1.  **`TELEGRAM_TOKEN`**: Dapatkan dari **[@BotFather](https://t.me/BotFather)** di Telegram.
2.  **`ADMIN_USER_ID`**: Dapatkan dari **[@userinfobot](https://t.me/userinfobot)**.
3.  **`GEMINI_API_KEY`**: Dapatkan dari **[Google AI Studio](https://aistudio.google.com/)**.
4.  **`credentials.json`**:
    * Buat proyek di **[Google Cloud Console](https://console.cloud.google.com/)**.
    * Aktifkan API: **Google Drive API**, **Google Docs API**, dan **Google Sheets API**.
    * Konfigurasi "OAuth consent screen" (pilih "External" dan tambahkan email Anda sebagai "Test user").
    * Buat kredensial "OAuth client ID" dengan tipe "Desktop app".
    * Unduh file JSON yang diberikan dan ganti namanya menjadi `credentials.json`.

#### A2. Siapkan Folder Proyek Lokal

1.  Buat folder proyek (misal: `MyRazenBot`) dan masukkan isi dari repository ini serta `credentials.json` yang sudah di dapatkan di awal.
2.  **Kloning Repositori ini di dalam folder proyek**
    ```bash
    git clone https://github.com/SEN9945/Razen-Bot.git
    cd Razen-Bot
    ```
3.  **Buat Virtual Environment & Install Dependensi**
    ```bash
    # Untuk Windows
    python -m venv .venv
    # Hasilnya Muncul File .\.venv\Scripts\activate

    # Untuk macOS/Linux
    python3 -m venv .venv
    # Hasilnya Muncul File .venv/bin/activate
    ```

#### A3. Jalankan Otentikasi untuk Menghasilkan `token.json`

1.  Buka terminal di folder proyek Anda.
2.  Buat dan aktifkan virtual environment, lalu jalankan `pip install -r requirements.txt`.
3.  Jalankan skrip otentikasi: `python authenticate_google.py`.
4.  Ikuti proses login di browser. Setelah selesai, file **`token.json`** akan muncul.

#### A4. Jalankan Bot di Komputer Lokal dengan command di terminal `python razen_bot.py`.
>Sekarang setelah semua file (termasuk yang rahasia) ada di lokal, kita unggah versi amannya ke GitHub.
1. **Buat Repositori Baru di GitHub:** Buka [GitHub](https://github.com/) dan buat repositori baru (misalnya, `RazenBot`). **Jangan** centang opsi untuk menambahkan `README` dan `.gitignore`.
2. Pastikan ada sudah menginstal git di komputer anda dengan cek `git -v`
```bash
git init
git add .
git commit -m "Initial commit of Razen Bot project"
git remote add origin [url repository]
git push origin main
```
> Pasrikan Struktur projek sudah sesuai dengan contoh
---
### Bagian B: Pemasangan di Server/VPS (Terminal Only)

#### B1. Persiapan Awal Server (Untuk Server Baru)

Jika Anda menggunakan server Ubuntu/Debian yang masih baru, jalankan perintah ini terlebih dahulu:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
```

#### B2. Siapkan Proyek di Server

1.  **Kloning Repositori dari GitHub Anda yang Sudah Dibuat Tadi**
    > **Penting:** Sebelum push ke GitHub, pastikan Anda sudah membuat file `.gitignore` di proyek lokal Anda agar file rahasia (`.env`, `credentials.json`, `token.json`, `.venv/`) tidak ikut terunggah!
    ```bash
    git clone https://github.com/NAMA_USER_ANDA/NAMA_REPO_ANDA.git
    cd NAMA_REPO_ANDA
    ```
2.  **Buat Virtual Environment & Install Dependensi**
    ```bash
    python3 -m venv .venv
    # Hasilnya Muncul File .venv/bin/activate
    pip install -r requirements.txt
    ```

#### B3. Pindahkan File Rahasia ke Server

Anda sekarang perlu memindahkan 3 file rahasia (`.env`, `credentials.json`, dan `token.json`) dari komputer lokal Anda ke folder proyek di server, baik menggunakan `scp` ataupun copy-paste manual.
* **Cara Manual Copy-Paste (Untuk Pemula)**
    Buka setiap file rahasia di komputer Anda, salin seluruh isinya. Lalu, di terminal server masuk ke folder repo `cd NAMA_REPO_ANDA`, gunakan editor teks seperti `nano` untuk membuat file baru dan tempel isinya.
    ```bash
    # Contoh untuk file .env
    nano .env
    # (Tempel konten, lalu tekan Ctrl+X, lalu Y, lalu Enter untuk menyimpan)
    ```
#### B4. Jalankan Bot Secara Terus-Menerus

Pilih salah satu metode di bawah ini untuk menjalankan bot Anda agar tetap online.

##### Metode 1: Sederhana (Menggunakan `screen`)
> Pilihan terbaik untuk pemula dan pengujian cepat.

1.  **Instal `screen` (jika belum ada):** `sudo apt install screen`
2.  **Buat sesi baru:** `screen -S razen`
3.  **Jalankan bot di dalam sesi:** `python razen_bot.py`
4.  **Keluar dari sesi:** Tekan `Ctrl+A` lalu `D`. Bot akan tetap berjalan.
5.  **Masuk kembali ke sesi:** `screen -r razen`.

##### Metode 2: Profesional (Menggunakan `pm2`)
> Pilihan terbaik untuk produksi karena memiliki fitur **restart otomatis** jika bot crash.

1.  **Instal Node.js dan npm:**
    ```bash
    curl -fsSL [https://deb.nodesource.com/setup_lts.x](https://deb.nodesource.com/setup_lts.x) | sudo -E bash -
    sudo apt-get install -y nodejs
    ```
2.  **Instal `pm2` secara global:**
    ```bash
    sudo npm install pm2 -g
    ```
3.  **Jalankan bot menggunakan `pm2`:**
    ```bash
    # Pastikan Anda berada di dalam folder proyek
    pm2 start razen_bot.py --name "razen" --interpreter python3
    ```
4.  **Perintah `pm2` yang berguna:**
    * `pm2 list`: Melihat status bot.
    * `pm2 logs razen`: Melihat log bot secara real-time.
    * `pm2 restart razen`: Memulai ulang bot.
    * `pm2 stop razen`: Menghentikan bot.

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
