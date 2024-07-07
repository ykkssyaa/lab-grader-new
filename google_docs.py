import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config_loader import GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE, LABS_SHEETS_RANGE

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

    return spreadsheet.get("values", [])[0]

