import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config_loader import (GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE, LABS_SHEETS_RANGE,
                           STUDENTS_SHEETS_RANGE, HEADERS_SHEETS_RANGE, GITHUB_HEADER)

creds = None

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

if os.path.exists(GOOGLE_TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE, SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            GOOGLE_CREDENTIALS_FILE, SCOPES
        )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(GOOGLE_TOKEN_FILE, "w") as token:
        token.write(creds.to_json())


def column_index_to_letter(index):
    """Convert a column index (0-based) to a letter (A, B, C, ..., AA, AB, ...)"""
    letters = ""
    while index >= 0:
        letters = chr(index % 26 + ord('A')) + letters
        index = index // 26 - 1
    return letters


def get_course_groups(google_spreadsheet_id: str) -> list[str]:
    if creds is None:
        print("get_course_groups: Credentials not loaded.")
        return []

    service = build("sheets", "v4", credentials=creds)
    spreadsheet = service.spreadsheets().get(spreadsheetId=google_spreadsheet_id).execute()

    sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]

    return sheets


def get_course_group_labs(google_spreadsheet_id: str, group: str) -> list[str]:
    if creds is None:
        print("get_course_groups: Credentials not loaded.")
        return []

    service = build("sheets", "v4", credentials=creds)
    spreadsheet_range = f"{group}!{LABS_SHEETS_RANGE}"

    spreadsheet = service.spreadsheets().values().get(
        spreadsheetId=google_spreadsheet_id,
        range=spreadsheet_range
    ).execute()

    return spreadsheet.get("values", [])


def get_students_of_group(google_spreadsheet_id: str, group: str) -> list[str]:
    if creds is None:
        print("get_users_of_group: Credentials not loaded.")
        return []

    service = build("sheets", "v4", credentials=creds)
    spreadsheet_range = f"{group}!{STUDENTS_SHEETS_RANGE}"

    spreadsheet = service.spreadsheets().values().get(
        spreadsheetId=google_spreadsheet_id,
        range=spreadsheet_range
    ).execute()

    return [row[0] for row in spreadsheet.get("values", [])]


def find_github_column(google_spreadsheet_id: str, group: str) -> str:
    if creds is None:
        print("find_github_column: Credentials not loaded.")
        return []

    service = build("sheets", "v4", credentials=creds)
    spreadsheet_range = f"{group}!{HEADERS_SHEETS_RANGE}"

    spreadsheet = service.spreadsheets().values().get(
        spreadsheetId=google_spreadsheet_id,
        range=spreadsheet_range
    ).execute()

    headers = spreadsheet.get("values", [])[0]

    try:
        index = headers.index(GITHUB_HEADER)
        return f"{column_index_to_letter(index)}"

    except ValueError:
        return None


def update_cell(google_spreadsheet_id: str, sheet: str, col: str, row: str, value: str, check_null: bool = False):

    if creds is None:
        print("update_cell: Credentials not loaded.")
        return []

    service = build("sheets", "v4", credentials=creds)
    cell = f"{sheet}!{col}{row}"

    if check_null:
        existing_value = service.spreadsheets().values().get(
            spreadsheetId=google_spreadsheet_id,
            range=cell
        ).execute().get("values", [[""]])[0][0]

        if existing_value == value:
            raise ValueError("Этот аккаунт GitHub уже был указан ранее для этого же студента. "
                             "Для изменения аккаунта обратитесь к преподавателю")
        elif existing_value is not None and existing_value != '':
            raise ValueError("Аккаунт GitHub уже был указан ранее. Для изменения аккаунта обратитесь к преподавателю")

    body = {
        "range": cell,
        "values": [
            [value]
        ]
    }

    result = service.spreadsheets().values().update(
        spreadsheetId=google_spreadsheet_id,
        range=cell,
        valueInputOption="RAW",
        body=body
    ).execute()

    print(f"Updated cell {cell} with value '{value}'")


def get_values_by_range(google_spreadsheet_id: str, spreadsheet_range: str):

    if creds is None:
        print("find_github_column: Credentials not loaded.")
        return []

    service = build("sheets", "v4", credentials=creds)

    spreadsheet = service.spreadsheets().values().get(
        spreadsheetId=google_spreadsheet_id,
        range=spreadsheet_range
    ).execute()

    return spreadsheet.get("values", [])