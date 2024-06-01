import os

Google_Key = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

# Google認証情報
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# JSON文字列

credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(Google_Key), scope
)


def a():
    # Google Drive APIのビルド
    drive_service = build("drive", "v3", credentials=credentials)

    # Google Drive内の全てのスプレッドシートを取得
    results = (
        drive_service.files().list(fields="nextPageToken, files(id, name)").execute()
    )

    # スプレッドシートの一覧を表示
    items = results.get("files", [])

    if not items:
        print("No files found.")
    else:
        print("Files:")
        for item in items:
            print(f"{item['name']} ({item['id']})")


def load_google_sheet(spreadsheet_url):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    gc = gspread.authorize(credentials)

    workbook = gc.open_by_url(spreadsheet_url)

    return workbook


sheet = load_google_sheet(
    "https://docs.google.com/spreadsheets/d/10EoTlXP4nGA8WUER1bpLXJBB99SNL7knAd577k2qM8Q/edit?usp=sharing"
)


def print_sheet_names(workbook):
    for sheet in workbook.worksheets():
        print(sheet.title)


print_sheet_names(sheet)
