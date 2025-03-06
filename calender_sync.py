import os
import pickle
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# ------------------------------
# Google Calendar Authentication
# ------------------------------
def authenticate_google_calendar():
    creds = None
    token_path = "token.pickle"
    
    # Load credentials if token file exists
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    # If credentials are invalid or missing, re-authenticate (User must manually get credentials.json)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("ERROR: Missing valid Google Calendar credentials. Run Google OAuth flow to get token.")
            return None
        
        # Save updated credentials
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return creds

# ------------------------------
# Sync Tasks with Google Calendar
# ------------------------------
def sync_with_calendar(tasks):
    creds = authenticate_google_calendar()
    if not creds:
        print("Google Calendar authentication failed.")
        return

    service = build("calendar", "v3", credentials=creds)

    for index, task in enumerate(tasks):
        event = {
            "summary": task,
            "start": {
                "dateTime": (datetime.utcnow() + timedelta(hours=index+1)).isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "end": {
                "dateTime": (datetime.utcnow() + timedelta(hours=index+2)).isoformat(),
                "timeZone": "Asia/Kolkata",
            },
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        print(f"Task '{task}' scheduled in Google Calendar: {created_event.get('htmlLink')}")

    print("All tasks synced successfully!")

# ------------------------------
# Debugging: Run Script Manually
# ------------------------------
if __name__ == "__main__":
    test_tasks = ["Complete AI project", "Workout session", "Prepare for meeting"]
    sync_with_calendar(test_tasks)
