import os
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError

# OAuth 2.0 scope for modifying Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def gmail_login():
    creds = None

    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception:
            print("⚠️ Failed to load token.json. Deleting and retrying login...")
            os.remove('token.json')
            return gmail_login()

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                print("⚠️ Token refresh failed. Deleting token.json and retrying login...")
                os.remove('token.json')
                return gmail_login()
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def delete_emails_by_category(service, category, user_id='me', max_to_delete=3999):
    query = f'category:{category}'
    print(f"🔍 Searching for emails in category: {category}...")

    count = 0
    next_page_token = None

    while count < max_to_delete:
        response = service.users().messages().list(
            userId=user_id,
            q=query,
            maxResults=min(100, max_to_delete - count),
            pageToken=next_page_token
        ).execute()

        messages = response.get('messages', [])

        if not messages:
            print("✅ No more emails found.")
            break  # No more emails, exit early

        for message in messages:
            service.users().messages().trash(userId=user_id, id=message['id']).execute()
            count += 1
            time.sleep(0.05)
            if count >= max_to_delete:
                break

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            print("✅ No more pages to fetch.")
            break  # No more pages, exit

    print(f"🗑️ {count} emails moved to Trash from category: {category}")

def main():
    service = gmail_login()
    categories = ['social']
    for cat in categories:
        delete_emails_by_category(service, cat)

if __name__ == '__main__':
    main()
