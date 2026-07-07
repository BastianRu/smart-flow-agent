import os
from datetime import datetime

from dotenv import load_dotenv, set_key, find_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

# Path to the .env file (used to persist refreshed tokens)
ENV_PATH = find_dotenv() or '.env'

SCOPES = ['https://www.googleapis.com/auth/calendar']


def _parse_expiry(token_expiry: str):
    if not token_expiry:
        return None
    try:
        return datetime.fromisoformat(token_expiry)
    except ValueError:
        try:
            return datetime.strptime(token_expiry, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None


def _persist_token(access_token: str, expiry: datetime | None):
    try:
        set_key(ENV_PATH, 'ACCESS_TOKEN', access_token)
        if expiry:
            set_key(ENV_PATH, 'TOKEN_EXPIRY', expiry.isoformat())
        else:
            set_key(ENV_PATH, 'TOKEN_EXPIRY', '')
    except Exception:
        # best-effort persistence; do not crash the app on failure
        print('Warning: no se pudo persistir el token en .env')


def get_credentials() -> Credentials:
    """Build Credentials from environment, refresh if needed, and persist updates."""
    access_token = os.getenv('ACCESS_TOKEN')
    refresh_token = os.getenv('REFRESH_TOKEN')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    token_expiry = os.getenv('TOKEN_EXPIRY')

    if not client_id or not client_secret:
        raise SystemExit('CLIENT_ID y CLIENT_SECRET are required in .env file')

    if not refresh_token:
        raise SystemExit('REFRESH_TOKEN is required in .env to regenerate token when it expires')

    expiry = _parse_expiry(token_expiry)

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri='https://oauth2.googleapis.com/token',
        expiry=expiry,
        scopes=SCOPES,
    )

    # Refresh if expired and persist new token values
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            print('Access token renewed:')
            print(creds.token)
            _persist_token(creds.token, creds.expiry)
        except Exception as e:
            # surface refresh errors clearly
            raise

    return creds


def get_calendar_service():
    creds = get_credentials()
    return build('calendar', 'v3', credentials=creds)
