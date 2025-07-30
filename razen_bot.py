# razen_bot.py

import os
import logging
import io
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes, ConversationHandler
)

# Peralatan Google
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import gspread

# Peralatan AI Gemini
import google.generativeai as genai

# --- Konfigurasi Awal & Keamanan ---
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_USER_ID_STR = os.getenv("ADMIN_USER_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

if not all([TELEGRAM_TOKEN, ADMIN_USER_ID_STR, GEMINI_API_KEY]):
    logger.critical("FATAL ERROR: Pastikan TELEGRAM_TOKEN, ADMIN_USER_ID, dan GEMINI_API_KEY ada di file .env")
    exit()

ADMIN_USER_ID = int(ADMIN_USER_ID_STR)
genai.configure(api_key=GEMINI_API_KEY)
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets"
]


# --- Fungsi Helper & Keamanan ---

def get_google_creds():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                 logger.error(f"Gagal memperbarui token. Perlu otentikasi ulang. Error: {e}")
                 return None
        else:
            logger.error("Kredensial Google tidak ditemukan. Jalankan authenticate_google.py")
            return None
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_service(service_name: str, version: str):
    creds = get_google_creds()
    if not creds: return None
    try:
        return build(service_name, version, credentials=creds)
    except HttpError as error:
        logger.error(f"Gagal membuat service {service_name}: {error}")
        return None

def get_sheets_client():
    creds = get_google_creds()
    if not creds: return None
    return gspread.authorize(creds)

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_USER_ID

def find_or_create_folder(drive_service, folder_name):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and 'root' in parents and trashed=false"
    response = drive_service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    files = response.get('files', [])
    if files:
        return files[0].get('id')
    else:
        file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

# --- ConversationHandler: Alur Upload File ---
(
    SELECTING_METHOD, SELECTING_MANUAL_ACTION, AWAITING_NEW_FOLDER_NAME,
    AWAITING_SEARCH_QUERY, SELECTING_SEARCH_RESULT, SELECTING_AUTO_FOLDER
) = range(6)
async def upload_entry_point(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_admin(update.message.from_user.id): return ConversationHandler.END
    file_obj = update.message.document or update.message.photo[-1] or update.message.video
    context.user_data['file_to_upload'] = {'file_id': file_obj.file_id, 'file_name': file_obj.file_name or f"file_{file_obj.file_unique_id}.jpg"}
    keyboard = [[InlineKeyboardButton("Simpan Otomatis 🗂️", callback_data='auto')], [InlineKeyboardButton("Simpan Manual ✍️", callback_data='manual')], [InlineKeyboardButton("Batal ❌", callback_data='cancel')]]
    await update.message.reply_text("File diterima. Bagaimana Anda ingin menyimpannya?", reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECTING_METHOD

async def select_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    action = query.data
    if action == 'auto':
        keyboard = [[InlineKeyboardButton("Dokumen 📄", callback_data='upload_final:Dokumen')], [InlineKeyboardButton("Foto & Video 🖼️", callback_data='upload_final:Foto & Video')], [InlineKeyboardButton("Catatan 📝", callback_data='upload_final:Catatan')], [InlineKeyboardButton("Lainnya 📦", callback_data='upload_final:Lainnya')]]
        await query.edit_message_text(text="Pilih kategori folder tujuan:", reply_markup=InlineKeyboardMarkup(keyboard))
        return SELECTING_AUTO_FOLDER
    elif action == 'manual':
        keyboard = [[InlineKeyboardButton("📂 Buat Folder Baru", callback_data='manual_new')], [InlineKeyboardButton("🔍 Cari Folder", callback_data='manual_search')]]
        await query.edit_message_text(text="Pilih aksi untuk mode manual:", reply_markup=InlineKeyboardMarkup(keyboard))
        return SELECTING_MANUAL_ACTION
    elif action == 'cancel':
        await query.edit_message_text(text="Proses upload dibatalkan.")
        return ConversationHandler.END

async def select_manual_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    action = query.data
    if action == 'manual_new':
        await query.edit_message_text(text="Baik, ketikkan nama untuk folder baru Anda:")
        return AWAITING_NEW_FOLDER_NAME
    elif action == 'manual_search':
        await query.edit_message_text(text="Baik, ketikkan nama folder yang ingin Anda cari:")
        return AWAITING_SEARCH_QUERY

async def new_folder_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    folder_name = update.message.text
    await update.message.reply_text(f"Membuat dan menyimpan ke folder baru '{folder_name}'...")
    drive_service = get_service('drive', 'v3')
    folder_id = find_or_create_folder(drive_service, folder_name)
    await upload_to_drive(update.effective_chat.id, context, folder_id)
    return ConversationHandler.END

async def search_folder_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query_text = update.message.text
    await update.message.reply_text(f"Mencari folder yang mengandung '{query_text}'...")
    drive_service = get_service('drive', 'v3')
    query = f"mimeType='application/vnd.google-apps.folder' and name contains '{query_text}' and trashed=false"
    response = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)', pageSize=10).execute()
    folders = response.get('files', [])
    if not folders:
        await update.message.reply_text("Tidak ada folder yang ditemukan. Silakan coba lagi atau batalkan dengan /cancel.")
        return AWAITING_SEARCH_QUERY
    keyboard = [[InlineKeyboardButton(f"📁 {folder['name']}", callback_data=f"select_folder:{folder['id']}")] for folder in folders]
    await update.message.reply_text("Berikut folder yang ditemukan. Silakan pilih satu:", reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECTING_SEARCH_RESULT

async def select_search_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    folder_id = query.data.split(':', 1)[1]
    await query.edit_message_text("Folder dipilih. Memproses upload...")
    await upload_to_drive(query.message.chat_id, context, folder_id)
    return ConversationHandler.END

async def auto_folder_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    folder_name = query.data.split(':', 1)[1]
    await query.edit_message_text(text=f"Menyimpan ke folder '{folder_name}'...")
    drive_service = get_service('drive', 'v3')
    folder_id = find_or_create_folder(drive_service, folder_name)
    await upload_to_drive(query.message.chat_id, context, folder_id)
    return ConversationHandler.END

async def upload_to_drive(chat_id: int, context: ContextTypes.DEFAULT_TYPE, folder_id: str):
    file_info = context.user_data.get('file_to_upload')
    if not file_info:
        await context.bot.send_message(chat_id, "Error: Info file hilang.")
        return
    try:
        drive_service = get_service('drive', 'v3')
        file_to_upload = await context.bot.get_file(file_info['file_id'])
        file_in_memory = io.BytesIO(await file_to_upload.download_as_bytearray())
        file_metadata = {'name': file_info['file_name'], 'parents': [folder_id]}
        media = MediaIoBaseUpload(file_in_memory, mimetype='application/octet-stream', resumable=True)
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='name, webViewLink').execute()
        success_message = f"✅ Berhasil! File <a href='{uploaded_file.get('webViewLink')}'>{uploaded_file.get('name')}</a> telah disimpan."
        await context.bot.send_message(chat_id, success_message, parse_mode='HTML', link_preview_options=LinkPreviewOptions(is_disabled=True))
    except Exception as e:
        logger.error(f"Error pada fungsi upload_to_drive: {e}")
        await context.bot.send_message(chat_id, "Oops, terjadi kesalahan saat mengunggah, namun file mungkin sudah tersimpan. Silakan periksa Drive.")
    if 'file_to_upload' in context.user_data:
        del context.user_data['file_to_upload']

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Aksi dibatalkan.")
    if 'file_to_upload' in context.user_data:
        del context.user_data['file_to_upload']
    return ConversationHandler.END

# --- Fitur Pencarian & Manajemen Docs ---
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id): return
    query_text = " ".join(context.args)
    if not query_text:
        await update.message.reply_text("Mohon berikan nama file/folder yang ingin dicari.\nContoh: `/cari Laporan`")
        return
    await update.message.reply_text(f"🔎 Mencari item yang mengandung '{query_text}'...")
    try:
        drive_service = get_service('drive', 'v3')
        query = f"name contains '{query_text}' and trashed = false"
        response = drive_service.files().list(q=query, pageSize=10, fields="files(id, name, mimeType)").execute()
        items = response.get('files', [])
        if not items:
            await update.message.reply_text("Tidak ada file atau folder yang ditemukan.")
            return
        keyboard = []
        for item in items:
            emoji = "📁" if 'folder' in item['mimeType'] else "📄"
            callback_action = f"search_select_folder:{item['id']}" if 'folder' in item['mimeType'] else f"search_select_file:{item['id']}"
            keyboard.append([InlineKeyboardButton(f"{emoji} {item['name']}", callback_data=callback_action)])
        await update.message.reply_text("Berikut item yang ditemukan:", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error di /cari: {e}")
        await update.message.reply_text("Oops, terjadi kesalahan saat melakukan pencarian.")

async def search_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.callback_query.from_user.id): return
    query = update.callback_query
    await query.answer()
    action, item_id = query.data.split(':', 1)
    if action == 'search_select_file':
        status_message = None
        try:
            drive_service = get_service('drive', 'v3')
            file_metadata = drive_service.files().get(fileId=item_id, fields='name').execute()
            file_name = file_metadata.get('name')
            status_message = await query.edit_message_text(text=f"Mengambil file '{file_name}'...")
            request = drive_service.files().get_media(fileId=item_id)
            file_in_memory = io.BytesIO()
            downloader = MediaIoBaseDownload(file_in_memory, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            file_in_memory.seek(0)
            await context.bot.send_document(chat_id=query.message.chat_id, document=file_in_memory, filename=file_name)
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=status_message.message_id)
        except Exception as e:
            logger.error(f"Error saat mengirim file dari pencarian: {e}")
            if status_message:
                await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=status_message.message_id, text=f"Oops, gagal mengirim file.")
    elif action == 'search_select_folder':
        try:
            drive_service = get_service('drive', 'v3')
            folder_metadata = drive_service.files().get(fileId=item_id, fields='name, webViewLink').execute()
            folder_name = folder_metadata.get('name')
            folder_link = folder_metadata.get('webViewLink')
            await query.edit_message_text(
                text=f"Anda memilih folder: <b>{folder_name}</b>\n\nSilakan buka tautan ini untuk melihat isinya:",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(text=f"Buka Folder 📁", url=folder_link)
                ]])
            )
        except Exception as e:
            logger.error(f"Error saat mengambil link folder: {e}")
            await query.edit_message_text(text="Oops, gagal mendapatkan informasi folder.")

async def create_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id): return
    try:
        full_text = " ".join(context.args)
        title, content = [part.strip() for part in full_text.split('|', 1)]
    except ValueError:
        await update.message.reply_text("Format salah. Gunakan: `/catat Judul | Isi`")
        return
    await update.message.reply_text(f"📝 Membuat catatan '{title}'...")
    try:
        docs_service = get_service('docs', 'v1')
        drive_service = get_service('drive', 'v3')
        if not docs_service or not drive_service:
            await update.message.reply_text("Gagal terhubung ke layanan Google.")
            return
        doc_body = {'title': title}
        doc = docs_service.documents().create(body=doc_body).execute()
        doc_id = doc.get('documentId')
        requests = [{'insertText': {'location': {'index': 1}, 'text': content}}]
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
        notes_folder_id = find_or_create_folder(drive_service, "Catatan")
        file = drive_service.files().get(fileId=doc_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        drive_service.files().update(fileId=doc_id, addParents=notes_folder_id, removeParents=previous_parents, fields='id, parents').execute()
        doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
        await update.message.reply_html(f"✅ Catatan <a href='{doc_link}'>{title}</a> berhasil dibuat.", link_preview_options=LinkPreviewOptions(is_disabled=True))
    except Exception as e:
        logger.exception("Gagal membuat catatan baru:")
        await update.message.reply_text("Oops, terjadi kesalahan.")

async def append_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id): return
    try:
        full_text = " ".join(context.args)
        title, content_to_append = [part.strip() for part in full_text.split('|', 1)]
    except ValueError:
        await update.message.reply_text("Format salah. Gunakan: `/tambahcatatan Judul | Teks tambahan`")
        return
    await update.message.reply_text(f"Mencari catatan '{title}' untuk ditambahkan...")
    try:
        drive_service = get_service('drive', 'v3')
        docs_service = get_service('docs', 'v1')
        if not drive_service or not docs_service:
            await update.message.reply_text("Gagal terhubung ke layanan Google.")
            return
        notes_folder_id = find_or_create_folder(drive_service, "Catatan")
        query = f"name='{title}' and '{notes_folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false"
        response = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = response.get('files', [])
        if not files:
            await update.message.reply_text(f"Maaf, saya tidak menemukan catatan dengan judul '{title}' di folder Catatan.")
            return
        doc_id = files[0].get('id')
        document = docs_service.documents().get(documentId=doc_id).execute()
        end_index = document.get('body').get('content')[-1].get('endIndex')
        requests = [{'insertText': {'location': {'index': end_index - 1}, 'text': f"\n{content_to_append}"}}]
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
        doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
        await update.message.reply_html(f"✅ Teks berhasil ditambahkan ke catatan <a href='{doc_link}'>{title}</a>.", link_preview_options=LinkPreviewOptions(is_disabled=True))
    except Exception as e:
        logger.exception(f"Gagal menambahkan ke catatan '{title}':")
        await update.message.reply_text("Oops, terjadi kesalahan saat menambahkan catatan.")

async def read_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id): return
    title = " ".join(context.args)
    if not title:
        await update.message.reply_text("Format salah. Gunakan: `/bacacatatan Judul Catatan`")
        return
    await update.message.reply_text(f"📖 Membaca catatan '{title}'...")
    try:
        drive_service = get_service('drive', 'v3')
        docs_service = get_service('docs', 'v1')
        if not drive_service or not docs_service:
            await update.message.reply_text("Gagal terhubung ke layanan Google.")
            return
        notes_folder_id = find_or_create_folder(drive_service, "Catatan")
        query = f"name='{title}' and '{notes_folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false"
        response = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = response.get('files', [])
        if not files:
            await update.message.reply_text(f"Maaf, saya tidak menemukan catatan dengan judul '{title}' di folder Catatan.")
            return
        doc_id = files[0].get('id')
        document = docs_service.documents().get(documentId=doc_id).execute()
        content = ""
        for element in document.get('body').get('content'):
            if 'paragraph' in element:
                for run in element.get('paragraph').get('elements'):
                    if 'textRun' in run:
                        content += run.get('textRun').get('content')
        if not content.strip():
            content = "[Dokumen ini kosong]"
        for i in range(0, len(content), 4000):
            await update.message.reply_text(content[i:i + 4000])
    except Exception as e:
        logger.exception(f"Gagal membaca catatan '{title}':")
        await update.message.reply_text("Oops, terjadi kesalahan saat membaca catatan.")

async def read_sheet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id): return
    try:
        sheet_name, worksheet_name = [part.strip() for part in " ".join(context.args).split('|', 1)]
    except ValueError:
        await update.message.reply_text("Format salah. Gunakan: `/bacasheet Nama Sheet | Nama Tab`")
        return

    await update.message.reply_text(f"📊 Membaca sheet '{sheet_name}', tab '{worksheet_name}'...")
    try:
        gc = get_sheets_client()
        if not gc:
            await update.message.reply_text("Gagal terhubung ke Google Sheets.")
            return
        
        spreadsheet = gc.open(sheet_name)
        worksheet = spreadsheet.worksheet(worksheet_name)
        records = worksheet.get_all_records()

        if not records:
            await update.message.reply_text("Sheet ini kosong.")
            return

        message = f"<b>Isi dari {sheet_name} - {worksheet_name}:</b>\n"
        message += "<pre>"
        headers = list(records[0].keys())
        message += " | ".join(headers) + "\n"
        message += "-" * (len(" | ".join(headers)) + 2) + "\n"
        for record in records:
            row_values = [str(record.get(h, '')) for h in headers]
            message += " | ".join(row_values) + "\n"
        message += "</pre>"

        for i in range(0, len(message), 4000):
            await update.message.reply_html(message[i:i + 4000])

    except gspread.SpreadsheetNotFound:
        await update.message.reply_text(f"Maaf, spreadsheet dengan nama '{sheet_name}' tidak ditemukan.")
    except gspread.WorksheetNotFound:
        await update.message.reply_text(f"Maaf, tab dengan nama '{worksheet_name}' tidak ditemukan di sheet '{sheet_name}'.")
    except Exception as e:
        logger.exception(f"Gagal membaca sheet '{sheet_name}':")
        await update.message.reply_text("Oops, terjadi kesalahan saat membaca sheet.")

async def calculate_sheet_total_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id): return
    try:
        sheet_name, worksheet_name, column_name = [part.strip() for part in " ".join(context.args).split('|')]
    except ValueError:
        await update.message.reply_text("Format salah. Gunakan: `/hitung Nama Sheet | Nama Tab | Nama Kolom`")
        return

    await update.message.reply_text(f"🧮 Menghitung total kolom '{column_name}' di '{worksheet_name}'...")
    try:
        gc = get_sheets_client()
        if not gc:
            await update.message.reply_text("Gagal terhubung ke Google Sheets.")
            return

        spreadsheet = gc.open(sheet_name)
        worksheet = spreadsheet.worksheet(worksheet_name)
        
        values = worksheet.col_values(worksheet.find(column_name).col)
        
        total = 0
        for val in values[1:]:
            try:
                total += float(val.replace(",", ""))
            except (ValueError, TypeError):
                continue

        await update.message.reply_text(f"Total dari kolom '{column_name}' adalah: <b>{total:,.2f}</b>", parse_mode='HTML')

    except gspread.SpreadsheetNotFound:
        await update.message.reply_text(f"Maaf, spreadsheet dengan nama '{sheet_name}' tidak ditemukan.")
    except gspread.WorksheetNotFound:
        await update.message.reply_text(f"Maaf, tab dengan nama '{worksheet_name}' tidak ditemukan.")
    except gspread.CellNotFound:
        await update.message.reply_text(f"Maaf, kolom dengan nama '{column_name}' tidak ditemukan.")
    except Exception as e:
        logger.exception(f"Gagal menghitung total sheet '{sheet_name}':")
        await update.message.reply_text("Oops, terjadi kesalahan saat menghitung total.")

# --- ConversationHandler: List Files ---
LISTING_FILES = range(1) # State

def generate_list_page(page: int, results: list, query: str) -> tuple[str, InlineKeyboardMarkup]:
    """Membantu membuat teks dan tombol untuk halaman daftar file."""
    items_per_page = 20
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    total_pages = -(-len(results) // items_per_page) # Ceiling division

    message = f"<b>Daftar file '{query}' (Halaman {page}/{total_pages}):</b>\n"
    page_results = results[start_index:end_index]

    for i, item in enumerate(page_results, start=start_index + 1):
        message += f"{i}. <a href=\"{item.get('webViewLink')}\">{item.get('name')}</a>\n"

    keyboard = []
    row = []
    if page > 1:
        row.append(InlineKeyboardButton("⬅️ Sebelumnya", callback_data=f"list_page:{page-1}"))
    row.append(InlineKeyboardButton("Tutup ❌", callback_data="list_page:cancel"))
    if page < total_pages:
        row.append(InlineKeyboardButton("Berikutnya ➡️", callback_data=f"list_page:{page+1}"))
    keyboard.append(row)

    return message, InlineKeyboardMarkup(keyboard)

async def list_files_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id): return ConversationHandler.END
    try:
        file_type_input = " ".join(context.args).lower()
    except IndexError:
        await update.message.reply_text("Format salah. Gunakan: `/list <tipe>`\nContoh: `/list dokumen`")
        return ConversationHandler.END

    mime_map = {
        "dokumen": "application/vnd.google-apps.document",
        "sheets": "application/vnd.google-apps.spreadsheet",
        "sheet": "application/vnd.google-apps.spreadsheet",
        "spreadsheets": "application/vnd.google-apps.spreadsheet",
        "presentasi": "application/vnd.google-apps.presentation",
        "gambar": "mimeType contains 'image/'",
        "foto": "mimeType contains 'image/'",
        "pdf": "application/pdf",
        "video": "mimeType contains 'video/'"
    }

    if file_type_input not in mime_map:
        await update.message.reply_text(f"Tipe file '{file_type_input}' tidak dikenali. Coba: dokumen, sheets, presentasi, gambar, pdf, video.")
        return ConversationHandler.END

    query_string = mime_map[file_type_input]
    # Handle special cases for image/video
    if "contains" not in query_string:
        query_string = f"mimeType='{query_string}'"

    await update.message.reply_text(f"🔎 Mencari semua file dengan tipe '{file_type_input}'...")

    try:
        drive_service = get_service('drive', 'v3')
        query = f"{query_string} and trashed=false"
        response = drive_service.files().list(q=query, pageSize=200, fields="files(name, webViewLink)").execute()
        files = response.get('files', [])

        if not files:
            await update.message.reply_text(f"Tidak ada file dengan tipe '{file_type_input}' ditemukan.")
            return ConversationHandler.END

        context.user_data['list_results'] = files
        context.user_data['list_query'] = file_type_input

        message, keyboard = generate_list_page(1, files, file_type_input)
        await update.message.reply_html(message, reply_markup=keyboard, link_preview_options=LinkPreviewOptions(is_disabled=True))
        return LISTING_FILES

    except Exception as e:
        logger.error(f"Error di /list: {e}")
        await update.message.reply_text("Oops, terjadi kesalahan saat mencari daftar file.")
        return ConversationHandler.END

async def list_page_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    action = query.data.split(':', 1)[1]

    if action == 'cancel':
        await query.edit_message_text("Daftar ditutup.")
        context.user_data.pop('list_results', None)
        context.user_data.pop('list_query', None)
        return ConversationHandler.END

    page = int(action)
    results = context.user_data.get('list_results', [])
    list_query = context.user_data.get('list_query', '')

    if not results:
        await query.edit_message_text("Error: Hasil daftar tidak ditemukan. Silakan mulai lagi dengan /list.")
        return ConversationHandler.END

    message, keyboard = generate_list_page(page, results, list_query)
    await query.edit_message_text(text=message, reply_markup=keyboard, parse_mode='HTML', link_preview_options=LinkPreviewOptions(is_disabled=True))
    return LISTING_FILES

async def cancel_list_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Aksi daftar dibatalkan.")
    context.user_data.pop('list_results', None)
    context.user_data.pop('list_query', None)
    return ConversationHandler.END

async def list_sheets_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id): return
    await update.message.reply_text("📑 Mengambil daftar semua Google Sheets dan tab-nya... Ini mungkin perlu beberapa saat.")
    try:
        drive_service = get_service('drive', 'v3')
        gc = get_sheets_client()
        if not drive_service or not gc:
            await update.message.reply_text("Gagal terhubung ke layanan Google.")
            return

        query = "mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
        response = drive_service.files().list(q=query, pageSize=50, fields="files(id, name, webViewLink)").execute()
        sheets = response.get('files', [])

        if not sheets:
            await update.message.reply_text("Tidak ada file Google Sheet yang ditemukan.")
            return

        message = "<b>Berikut adalah daftar semua Google Sheets Anda:</b>\n\n"
        for sheet_file in sheets:
            message += f"📄 <b><a href=\"{sheet_file.get('webViewLink')}\">{sheet_file.get('name')}</a></b>\n"
            try:
                spreadsheet = gc.open_by_key(sheet_file.get('id'))
                worksheets = spreadsheet.worksheets()
                for ws in worksheets:
                    message += f"    - <i>{ws.title}</i>\n"
            except Exception as e:
                logger.error(f"Gagal membuka atau membaca worksheet dari {sheet_file.get('name')}: {e}")
                message += "    - <i>(Tidak bisa membaca tab)</i>\n"
            message += "\n"

        for i in range(0, len(message), 4000):
            await update.message.reply_html(message[i:i+4000], link_preview_options=LinkPreviewOptions(is_disabled=True))

    except Exception as e:
        logger.error(f"Error di /listsheets: {e}")
        await update.message.reply_text("Oops, terjadi kesalahan saat mengambil daftar sheet.")

# --- Manajemen Google Sheets ---
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id): return
    try:
        category = context.args[0]
        amount = int(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text("Format salah. Gunakan: `/lapor <Kategori> <Jumlah>`\nContoh: `/lapor Makanan 50000`")
        return
    await update.message.reply_text(f"📊 Mencatat '{category}' sebesar {amount}...")
    try:
        gc = get_sheets_client()
        if not gc:
            await update.message.reply_text("Gagal terhubung ke Google Sheets.")
            return
        try:
            spreadsheet = gc.open("Laporan Keuangan Razen")
        except gspread.SpreadsheetNotFound:
            spreadsheet = gc.create("Laporan Keuangan Razen")
            user_email = os.getenv("YOUR_GOOGLE_EMAIL")
            if user_email:
                spreadsheet.share(user_email, perm_type='user', role='writer')
        worksheet_title = datetime.now().strftime("%B %Y")
        try:
            worksheet = spreadsheet.worksheet(worksheet_title)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows="100", cols="20")
            worksheet.append_row(["Tanggal & Waktu", "Kategori", "Jumlah"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = [timestamp, category, amount]
        worksheet.append_row(new_row)
        sheet_link = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
        await update.message.reply_html(f"✅ Berhasil! Data telah dicatat di sheet <a href='{sheet_link}'>{worksheet_title}</a>.", link_preview_options=LinkPreviewOptions(is_disabled=True))
    except Exception as e:
        logger.exception("Gagal mencatat ke Google Sheets:")
        await update.message.reply_text("Oops, terjadi kesalahan saat mencatat ke spreadsheet.")

# --- Otak AI Gemini ---
def get_ai_response(user_message: str) -> dict:
    """Mengirim pesan ke Gemini dan mengembalikan respons dalam format JSON."""
    try:
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )

        system_prompt = '''
Anda adalah AI pemroses bahasa alami untuk bot Telegram bernama Razen. Tugas utama Anda adalah secara cerdas menerjemahkan pesan bahasa sehari-hari dari pengguna menjadi perintah JSON yang terstruktur dan dapat dieksekusi oleh bot.

**Proses Berpikir Anda:**
1.  **Analisis Niat Pengguna:** Baca pesan pengguna dengan cermat. Apa tujuan utama pengguna? Apakah mereka ingin mencari sesuatu, membuat, menambah, membaca, atau mencatat keuangan?
2.  **Identifikasi Fungsi:** Berdasarkan niat tersebut, pilih SATU fungsi yang paling sesuai dari daftar di bawah ini.
3.  **Ekstrak Parameter:** Setelah memilih fungsi, ekstrak informasi yang relevan dari pesan pengguna untuk mengisi parameter fungsi tersebut. Abaikan kata-kata pengisi (seperti "tolong", "bisakah kamu", "carikan saya") dan fokus pada kata kunci utama.
4.  **Bentuk JSON:** Buat respons HANYA dalam format JSON yang valid, berisi "function" dan "parameters". Jangan tambahkan penjelasan atau teks lain di luar JSON.

**Fungsi yang Tersedia:**

1.  `search_drive`
    - Deskripsi: Mencari file atau folder di Google Drive.
    - Parameter: `query` (string) - Kata kunci pencarian.
    - **Contoh Variatif:**
        - "carikan file stike ataupun cari file bernama stiker" -> `{"function": "search_drive", "parameters": {"query": "stiker"}}`
        - "di mana ya file laporan keuangan 2024?" -> `{"function": "search_drive", "parameters": {"query": "laporan keuangan 2024"}}`
        - "search Laporan Bulanan" -> `{"function": "search_drive", "parameters": {"query": "Laporan Bulanan"}}`

2.  `create_note`
    - Deskripsi: Membuat catatan baru di Google Docs.
    - Parameter: `title` (string), `content` (string, opsional).
    - **Contoh Variatif:**
        - "buat catatan judulnya Rencana Meeting isinya bahas proyek A" -> `{"function": "create_note", "parameters": {"title": "Rencana Meeting", "content": "bahas proyek A"}}`
        - "tolong catat ide baru: Kembangkan fitur AI untuk analisis data" -> `{"function": "create_note", "parameters": {"title": "Ide Baru", "content": "Kembangkan fitur AI untuk analisis data"}}`
        - "catat: Rapat Penting | Jangan lupa bahas anggaran" -> `{"function": "create_note", "parameters": {"title": "Rapat Penting", "content": "Jangan lupa bahas anggaran"}}`

3.  `append_note`
    - Deskripsi: Menambahkan teks ke catatan yang sudah ada.
    - Parameter: `title` (string), `content` (string).
    - **Contoh Variatif:**
        - "tambahkan ke catatan Rencana Meeting: jangan lupa undang tim B" -> `{"function": "append_note", "parameters": {"title": "Rencana Meeting", "content": "jangan lupa undang tim B"}}`
        - "lanjutkan catatan 'Daftar Tugas', tambahkan 'Beli susu'" -> `{"function": "append_note", "parameters": {"title": "Daftar Tugas", "content": "Beli susu"}}`

4.  `read_note`
    - Deskripsi: Membaca isi dari sebuah catatan.
    - Parameter: `title` (string).
    - **Contoh Variatif:**
        - "baca catatan Rencana Meeting" -> `{"function": "read_note", "parameters": {"title": "Rencana Meeting"}}`
        - "apa isi dari notulen rapat kemarin?" -> `{"function": "read_note", "parameters": {"title": "notulen rapat kemarin"}}`

5.  `log_expense`
    - Deskripsi: Mencatat pengeluaran ke Google Sheets.
    - Parameter: `category` (string), `amount` (integer).
    - **Contoh Variatif:**
        - "catat pengeluaran makan siang 50000" -> `{"function": "log_expense", "parameters": {"category": "Makan Siang", "amount": 50000}}`
        - "tadi beli bensin 150 ribu" -> `{"function": "log_expense", "parameters": {"category": "Transportasi", "amount": 150000}}`
        - "pengeluaran untuk belanja bulanan totalnya 750000" -> `{"function": "log_expense", "parameters": {"category": "Belanja Bulanan", "amount": 750000}}`

6.  `read_sheet`
    - Deskripsi: Membaca isi dari worksheet (tab) tertentu dalam sebuah Google Sheet.
    - Parameter: `sheet_name` (string), `worksheet_name` (string).
    - **Contoh Variatif:**
        - "baca laporan keuangan bulan juli" -> `{"function": "read_sheet", "parameters": {"sheet_name": "Laporan Keuangan Razen", "worksheet_name": "Juli 2025"}}`
        - "tampilkan isi dari sheet utama di file Anggaran Proyek" -> `{"function": "read_sheet", "parameters": {"sheet_name": "Anggaran Proyek", "worksheet_name": "Sheet1"}}`

7.  `calculate_total`
    - Deskripsi: Menghitung jumlah total dari sebuah kolom angka dalam worksheet.
    - Parameter: `sheet_name` (string), `worksheet_name` (string), `column_name` (string).
    - **Contoh Variatif:**
        - "berapa total pengeluaran bulan ini?" -> `{"function": "calculate_total", "parameters": {"sheet_name": "Laporan Keuangan Razen", "worksheet_name": "Juli 2025", "column_name": "Jumlah"}}`
        - "hitung total biaya di sheet Anggaran Proyek" -> `{"function": "calculate_total", "parameters": {"sheet_name": "Anggaran Proyek", "worksheet_name": "Sheet1", "column_name": "Biaya"}}`

8.  `list_files`
    - Deskripsi: Menampilkan daftar file berdasarkan tipenya.
    - Parameter: `file_type` (string) - Tipe file (dokumen, sheets, presentasi, gambar, pdf, video).
    - **Contoh Variatif:**
        - "tampilkan semua dokumen" -> `{"function": "list_files", "parameters": {"file_type": "dokumen"}}`
        - "kasih liat daftar sheet yang ada" -> `{"function": "list_files", "parameters": {"file_type": "sheets"}}`

9.  `list_all_sheets`
    - Deskripsi: Menampilkan daftar semua file Google Sheets beserta semua worksheet (tab) di dalamnya.
    - Parameter: Tidak ada.
    - **Contoh Variatif:**
        - "tampilkan semua sheet yang saya punya" -> `{"function": "list_all_sheets", "parameters": {}}`
        - "kasih liat daftar lengkap spreadsheet" -> `{"function": "list_all_sheets", "parameters": {}}`

**Aturan Ketat:**
- Jika permintaan pengguna SANGAT tidak jelas dan tidak bisa dipetakan ke fungsi mana pun setelah analisis terbaik Anda, gunakan fungsi `unknown`.
- `{"function": "unknown", "parameters": {"reason": "Saya tidak mengerti maksud Anda, mohon perjelas."}}`
- Selalu berikan respons dalam format JSON. Tanpa kecuali.
'''
        full_prompt = f"{system_prompt}\nPesan Pengguna: \"{user_message}\"\nRespons Anda:"

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        response = model.generate_content(full_prompt, safety_settings=safety_settings)

        if not response.parts:
            logger.warning(f"AI response was empty or blocked. Feedback: {response.prompt_feedback}")
            return {"function": "unknown", "parameters": {"reason": "AI tidak memberikan respons karena filter keamanan."}}

        return json.loads(response.text)

    except json.JSONDecodeError as e:
        logger.error(f"Gagal mem-parsing JSON dari AI: {e}")
        logger.error(f"Teks respons yang gagal diparsing: {response.text}")
        return {"function": "unknown", "parameters": {"reason": "AI memberikan respons dalam format yang tidak valid."}}
    except Exception as e:
        logger.exception("Terjadi kesalahan tak terduga saat berkomunikasi dengan Gemini:")
        return {"function": "unknown", "parameters": {"reason": "Terjadi kesalahan internal pada AI."}}


async def handle_natural_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id): return
    user_text = update.message.text
    status_msg = await update.message.reply_text("🤔 Razen sedang berpikir...")

    try:
        ai_decision = get_ai_response(user_text)
        await context.bot.delete_message(chat_id=status_msg.chat_id, message_id=status_msg.message_id)

        function_name = ai_decision.get("function")
        parameters = ai_decision.get("parameters", {})

        function_map = {
            "search_drive": (search_command, lambda p: p.get("query", "").split()),
            "create_note": (create_note_command, lambda p: f"{p.get('title', 'Tanpa Judul')} | {p.get('content', '')}".split(' | ', 1)),
            "append_note": (append_note_command, lambda p: f"{p.get('title', '')} | {p.get('content', '')}".split(' | ', 1)),
            "read_note": (read_note_command, lambda p: p.get("title", "").split()),
            "log_expense": (report_command, lambda p: [str(p.get("category", "Lainnya")), str(p.get("amount", 0))]),
            "read_sheet": (read_sheet_command, lambda p: f"{p.get('sheet_name', '')}|{p.get('worksheet_name', '')}".split('|')),
            "calculate_total": (calculate_sheet_total_command, lambda p: f"{p.get('sheet_name', '')}|{p.get('worksheet_name', '')}|{p.get('column_name', 'Jumlah')}".split('|')),
            "list_files": (list_files_command, lambda p: [p.get("file_type", "")]),
            "list_all_sheets": (list_sheets_command, lambda p: [])
        }

        if function_name in function_map:
            handler_function, args_builder = function_map[function_name]
            context.args = args_builder(parameters)
            await handler_function(update, context)
        elif function_name == "unknown":
            reason = parameters.get('reason', 'Saya tidak mengerti.')
            await update.message.reply_text(f"Maaf, {reason}")
        else:
            await update.message.reply_text("Maaf, AI memberikan respons yang tidak saya kenali.")

    except Exception as e:
        logger.error(f"Error di handle_natural_language: {e}")
        await context.bot.delete_message(chat_id=status_msg.chat_id, message_id=status_msg.message_id)
        await update.message.reply_text("Oops, terjadi kesalahan internal saat memproses permintaan Anda.")

# --- Perintah Umum ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id): return
    help_text = (
        "<b>Selamat Datang, Admin! Saya adalah Razen, Asisten Pribadi Google Anda.</b>\n\n"
        "Saya dapat membantu Anda mengelola file, catatan, dan laporan langsung dari Telegram. Anda bisa memberi saya perintah menggunakan format garis miring (/) atau berbicara langsung dalam bahasa biasa.\n\n"
        "--- <b>Perintah Manual</b> ---\n\n"
        "<b>Manajemen File & Drive:</b>\n"
        "• `/cari &lt;kata_kunci&gt;` - Mencari file atau folder di Google Drive.\n"
        "• `/list &lt;tipe&gt;` - Menampilkan daftar file berdasarkan tipe. Tipe yang didukung: `dokumen`, `sheets`, `presentasi`, `gambar`, `pdf`, `video`.\n"
        "• `/listsheets` - Menampilkan semua file Google Sheets beserta semua tab di dalamnya.\n\n"
        "<b>Manajemen Catatan (Google Docs):</b>\n"
        "• `/catat &lt;Judul&gt; | &lt;Isi catatan&gt;` - Membuat catatan baru.\n"
        "• `/tambahcatatan &lt;Judul&gt; | &lt;Teks tambahan&gt;` - Menambah teks ke catatan yang ada.\n"
        "• `/bacacatatan &lt;Judul&gt;` - Membaca isi dari sebuah catatan.\n\n"
        "<b>Manajemen Laporan (Google Sheets):</b>\n"
        "• `/lapor &lt;Kategori&gt; &lt;Jumlah&gt;` - Mencatat pengeluaran baru. Contoh: `/lapor Makanan 50000`\n"
        "• `/bacasheet &lt;Nama Sheet&gt; | &lt;Nama Tab&gt;` - Membaca isi dari sebuah tab di spreadsheet.\n"
        "• `/hitung &lt;Nama Sheet&gt; | &lt;Nama Tab&gt; | &lt;Nama Kolom&gt;` - Menghitung total dari sebuah kolom.\n\n"
        "--- <b>Kekuatan AI (Bahasa Natural)</b> ---\n\n"
        "Cukup tuliskan apa yang Anda butuhkan, dan saya akan mencoba memahaminya. Berikut beberapa contoh:\n\n"
        "- <i>\"Razen, carikan saya file presentasi Q3\"</i>\n"
        "- <i>\"tampilkan semua file pdf saya\"</i>\n"
        "- <i>\"buat catatan rapat penting hari ini isinya adalah...\"</i>\n"
        "- <i>\"tambahkan ke daftar belanja: beli telur dan roti\"</i>\n"
        "- <i>\"apa isi catatan proyek alpha?\"</i>\n"
        "- <i>\"catat pengeluaran transportasi 150000\"</i>\n"
        "- <i>\"baca laporan keuangan bulan lalu\"</i>\n"
        "- <i>\"berapa total pengeluaran untuk makanan bulan ini?\"</i>\n\n"
        "--- \n\n"
        "Kirim atau teruskan file (dokumen, foto, video) ke chat ini untuk memulai proses penyimpanan ke Google Drive.\n\n"
        "<i>Bot by @iceskey/SEN9945</i>"
    )
    await update.message.reply_text(text=help_text, parse_mode='HTML', link_preview_options=LinkPreviewOptions(is_disabled=True))

# --- Fungsi Utama untuk Menjalankan Bot ---
def main():
    logger.info("Memulai bot Razen...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    upload_conversation = ConversationHandler(
        entry_points=[MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO, upload_entry_point)],
        states={
            SELECTING_METHOD: [CallbackQueryHandler(select_method)],
            SELECTING_MANUAL_ACTION: [CallbackQueryHandler(select_manual_action)],
            AWAITING_NEW_FOLDER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_folder_input)],
            AWAITING_SEARCH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_folder_input)],
            SELECTING_SEARCH_RESULT: [CallbackQueryHandler(select_search_result, pattern=r'^select_folder:')],
            SELECTING_AUTO_FOLDER: [CallbackQueryHandler(auto_folder_selection, pattern=r'^upload_final:')]
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)]
    )

    list_conversation = ConversationHandler(
        entry_points=[CommandHandler("list", list_files_command)],
        states={
            LISTING_FILES: [CallbackQueryHandler(list_page_handler, pattern=r'^list_page:')]
        },
        fallbacks=[CommandHandler('cancel', cancel_list_conversation)]
    )
    
    application.add_handler(upload_conversation)
    application.add_handler(list_conversation)
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("cari", search_command))
    application.add_handler(CommandHandler("catat", create_note_command))
    application.add_handler(CommandHandler("tambahcatatan", append_note_command))
    application.add_handler(CommandHandler("bacacatatan", read_note_command))
    application.add_handler(CommandHandler("bacasheet", read_sheet_command))
    application.add_handler(CommandHandler("hitung", calculate_sheet_total_command))
    application.add_handler(CommandHandler("listsheets", list_sheets_command))
    application.add_handler(CommandHandler("lapor", report_command))

    application.add_handler(CallbackQueryHandler(search_button_handler, pattern=r'^search_select_'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_natural_language))

    logger.info("Terimakasi sudah menggunakan Razen Bot. Bot sedang berjalan. Tekan Ctrl+C untuk berhenti.")
    application.run_polling()

if __name__ == '__main__':
    main()
