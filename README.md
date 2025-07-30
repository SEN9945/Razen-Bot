# Razen - Asisten Pribadi Cerdas Bertenaga AI

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<p align="center">
  <img src="https://i.imgur.com/8Qz5Q7x.png" alt="Arsitektur Razen" width="600"/>
</p>

**Razen** adalah sebuah bot asisten pribadi Telegram yang cerdas, dirancang untuk menjadi jembatan antara percakapan sehari-hari Anda dengan ekosistem produktivitas Google Workspace. Ditenagai oleh **Google Gemini AI**, Razen mampu memahami perintah dalam bahasa natural dan mengeksekusi berbagai tugas, mulai dari manajemen file di Google Drive, membuat catatan di Google Docs, hingga mencatat pengeluaran di Google Sheets.

---

## ✨ Fitur Utama

Razen dilengkapi dengan serangkaian fitur canggih yang dirancang untuk meningkatkan produktivitas Anda:

* 🧠 **Otak AI Cerdas:**
    * Memahami perintah dalam bahasa natural berkat integrasi dengan **Google Gemini AI (`gemini-2.5-flash`)**.
    * Tidak perlu menghafal perintah kaku, cukup ajak Razen bicara seperti biasa.

* 🔒 **Keamanan Maksimal:**
    * Akses bot sepenuhnya terbatas pada **User ID** yang telah diotorisasi, memastikan hanya Anda yang dapat mengendalikannya.

* 🗂️ **Manajemen Google Drive:**
    * **Upload Canggih:** Kirim file apa saja dan Razen akan menawarkan opsi penyimpanan otomatis (berdasarkan kategori) atau manual (ke folder baru atau yang sudah ada).
    * **Pencarian Interaktif:** Cari file dan folder dengan bahasa natural. Hasil akan ditampilkan dalam bentuk tombol yang bisa dipilih.
    * **Kirim File:** Minta file dari hasil pencarian dan Razen akan mengirimkannya langsung ke Anda.

* ✍️ **Manajemen Google Docs:**
    * **Buat Catatan:** Buat dokumen baru di folder "Catatan" dengan cepat.
    * **Tambah Catatan:** Lanjutkan tulisan pada dokumen yang sudah ada tanpa perlu membuat file baru.
    * **Baca Catatan:** Minta Razen untuk membacakan isi dari catatan yang tersimpan.

* 📊 **Manajemen Google Sheets:**
    * **Catat Pengeluaran:** Laporkan pengeluaran harian dengan mudah (`/lapor Makanan 50000`), dan Razen akan mencatatnya di spreadsheet "Laporan Keuangan" secara otomatis.

---

## 🚀 Panduan Memulai

Ikuti langkah-langkah di bawah ini untuk menjalankan Razen di server atau komputer lokal Anda.

### Prasyarat

* Python 3.10 atau versi lebih baru.
* Akun Telegram.
* Akun Google.

### Panduan Instalasi

1.  **Kloning Repositori**
    ```bash
    git clone [https://github.com/NAMA_USER_ANDA/NAMA_REPO_ANDA.git](https://github.com/NAMA_USER_ANDA/NAMA_REPO_ANDA.git)
    cd NAMA_REPO_ANDA
    ```

2.  **(Sangat Direkomendasikan) Buat Virtual Environment**
    Ini akan mengisolasi dependensi proyek Anda dan mencegah konflik.
    ```bash
    # Untuk Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # Untuk macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instalasi Dependensi**
    Buat file bernama `requirements.txt` di dalam folder proyek Anda, salin konten di bawah ini ke dalamnya, lalu jalankan perintah `pip`.

    **`requirements.txt`:**
    ```text
    python-telegram-bot
    python-dotenv
    google-api-python-client
    google-auth-httplib2
    google-auth-oauthlib
    gspread
    google-generativeai
    ```

    **Jalankan perintah instalasi:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Konfigurasi Kunci API & Kredensial**
    Ini adalah langkah paling penting. Anda memerlukan 4 kunci rahasia.

    * **`TELEGRAM_TOKEN`**: Dapatkan dari **@BotFather** di Telegram dengan membuat bot baru.
    * **`ADMIN_USER_ID`**: Dapatkan User ID Telegram Anda dari **@userinfobot**.
    * **`GEMINI_API_KEY`**: Dapatkan dari **Google AI Studio**.
    * **`credentials.json`**:
        1.  Buat proyek di **Google Cloud Console**.
        2.  Aktifkan API: **Google Drive API**, **Google Docs API**, dan **Google Sheets API**.
        3.  Konfigurasi "OAuth consent screen" (pilih "External" dan tambahkan email Anda sebagai "Test user").
        4.  Buat kredensial baru dengan tipe "OAuth client ID" dan pilih "Desktop app".
        5.  Unduh file JSON yang dihasilkan dan ganti namanya menjadi `credentials.json`. Letakkan di folder utama proyek.

    Buat file bernama `.env` di folder utama proyek dan isi dengan format berikut:
    ```env
    TELEGRAM_TOKEN="TOKEN_TELEGRAM_ANDA"
    ADMIN_USER_ID="USER_ID_TELEGRAM_ANDA"
    GEMINI_API_KEY="KUNCI_API_GEMINI_ANDA"
    YOUR_GOOGLE_EMAIL="emailanda@gmail.com" # Opsional, untuk membagikan Sheet ke diri sendiri
    ```

5.  **Otentikasi Google Pertama Kali**
    Kita perlu menjalankan skrip satu kali untuk menghasilkan `token.json` yang akan digunakan bot. Pastikan file `credentials.json` sudah ada.

    Jalankan skrip berikut di terminal:
    ```bash
    python authenticate_google.py
    ```
    Sebuah tab browser akan terbuka. Ikuti proses login dan berikan semua izin yang diminta. Setelah selesai, file `token.json` akan muncul di folder proyek Anda.

### Cara Menjalankan Bot

Setelah semua instalasi dan konfigurasi selesai, jalankan bot dengan perintah sederhana:
```bash
python razen_bot.py
```
Bot Anda sekarang sudah aktif! Buka Telegram dan mulailah berinteraksi dengannya.

---

## 🤖 Contoh Penggunaan

* **Perintah Spesifik:**
    * `/start` - Menampilkan pesan bantuan.
    * `/cari Laporan Keuangan` - Mencari file/folder.
    * `/catat Rapat Penting | Hasil rapat adalah...` - Membuat catatan baru.
    * `/tambahcatatan Rapat Penting | Tambahan: ...` - Menambah ke catatan.
    * `/bacacatatan Rapat Penting` - Membaca isi catatan.
    * `/lapor Makanan 50000` - Mencatat pengeluaran.

* **Percakapan Natural (AI):**
    * "Razen, tolong carikan aku presentasi proyek alfa"
    * "catat ide baru dengan isi: coba integrasi Google Calendar"
    * "tambahkan ke daftar belanja: beli buah-buahan"
    * "apa isi dari catatan rapat kemarin?"
    * "baru saja keluar uang 35000 untuk bensin"

---

## 🗺️ Peta Jalan (Roadmap)

Razen masih terus berkembang. Berikut adalah beberapa fitur yang direncanakan untuk masa depan:

* [ ] **Pengiriman Folder (Tahap D):** Mengimplementasikan logika kompresi (zip) dan pengiriman folder dari hasil pencarian.
* [ ] **Integrasi Google Calendar:** Menambahkan kemampuan untuk membuat dan mengelola agenda.
* [ ] **Interaksi yang Lebih Kontekstual:** Membuat AI mampu mengingat percakapan sebelumnya.

---

## 📜 Lisensi

Proyek ini didistribusikan di bawah Lisensi MIT. Lihat `LICENSE` untuk informasi lebih lanjut.
