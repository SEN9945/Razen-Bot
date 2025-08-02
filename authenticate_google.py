import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

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

if __name__ == "__main__":
    main()
