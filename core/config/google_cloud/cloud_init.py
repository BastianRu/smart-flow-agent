import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

DEFAULT_SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send',
    ]

load_dotenv()

client_secret_path = Path("client_secret_local.json")

if client_secret_path.exists():
    client_config = json.loads(client_secret_path.read_text(encoding="utf-8"))
else:
    client_config = {
        "web": {
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost", "http://127.0.0.1"],
        }
    }

flow = InstalledAppFlow.from_client_config(
    client_config,
    scopes=DEFAULT_SCOPES,
)

creds = flow.run_local_server(
    port=0,
    open_browser=True,
    authorization_url_params={"access_type": "offline", "prompt": "consent"},
)

print("access_token:", creds.token)
print("refresh_token:", creds.refresh_token)