import os
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://mail.google.com/']

def gmail_login():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                print("⚠️ Token refresh failed. Removing token.json and restarting login.")
                os.remove('token.json')
                return gmail_login()
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def fetch_all_message_ids(service, query):
    msg_ids = []
    next_page_token = None

    while True:
        response = service.users().messages().list(
            userId='me',
            q=query,
            pageToken=next_page_token,
            maxResults=500
        ).execute()

        msgs = response.get('messages', [])
        msg_ids.extend([msg['id'] for msg in msgs])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return msg_ids

def delete_emails_by_category(service, category):
    print(f"\n🔍 Checking for emails in category: {category}...")
    try:
        query = f"category:{category}"
        msg_ids = fetch_all_message_ids(service, query)

        if not msg_ids:
            print(f"✅ No emails found in category: {category}. Moving to next category.")
            return

        total_deleted = 0
        for i in range(0, len(msg_ids), 1000):
            batch = msg_ids[i:i + 1000]
            service.users().messages().batchDelete(userId='me', body={'ids': batch}).execute()
            total_deleted += len(batch)

        print(f"🗑️ {total_deleted} emails moved to Trash from category: {category}")

    except HttpError as error:
        print(f"❌ Error while deleting emails from {category}: {error}")

def empty_trash(service):
    print("\n♻️ Emptying Trash folder...")
    try:
        msg_ids = fetch_all_message_ids(service, "in:trash")

        if not msg_ids:
            print("✅ Trash is already empty.")
            return

        total_deleted = 0
        for i in range(0, len(msg_ids), 1000):
            batch = msg_ids[i:i + 1000]
            service.users().messages().batchDelete(userId='me', body={'ids': batch}).execute()
            total_deleted += len(batch)
            print(f"🧹 Deleted {len(batch)} messages from Trash...")

        print(f"✅ Total {total_deleted} messages permanently deleted from Trash.")

    except HttpError as error:
        print(f"❌ Failed to empty trash: {error}")

if __name__ == '__main__':
    service = gmail_login()

    for category in ['promotions', 'updates', 'social']:
        delete_emails_by_category(service, category)
        time.sleep(0.5)  # Tiny delay for clarity

    empty_trash(service)
    print("\n✅ Gmail cleanup completed successfully.\n")
