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

def get_user_category_choice():
    """Prompt user to select which email category to delete"""
    print("\n📧 Gmail Cleanup Tool")
    print("=" * 40)
    print("Available categories to clean up:")
    print("1. Primary")
    print("2. Promotions")
    print("3. Updates") 
    print("4. Social")
    print("5. All categories")
    print("6. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            if choice == '1':
                return ['primary']
            elif choice == '2':
                return ['promotions']
            elif choice == '3':
                return ['updates']
            elif choice == '4':
                return ['social']
            elif choice == '5':
                return ['primary', 'promotions', 'updates', 'social']
            elif choice == '6':
                print("👋 Goodbye!")
                return None
            else:
                print("❌ Invalid choice. Please enter a number between 1-6.")
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user.")
            return None

def ask_empty_trash():
    """Ask user if they want to empty the trash"""
    while True:
        try:
            choice = input("\n🗑️ Do you want to empty the Trash folder? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            else:
                print("❌ Please enter 'y' for yes or 'n' for no.")
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user.")
            return False

if __name__ == '__main__':
    try:
        service = gmail_login()
        
        while True:
            # Get user's category choice
            categories = get_user_category_choice()
            if not categories:
                break
            
            # Process selected categories
            for category in categories:
                delete_emails_by_category(service, category)
                time.sleep(0.5)  # Tiny delay for clarity
            
            # Ask if user wants to empty trash
            if ask_empty_trash():
                empty_trash(service)
            else:
                print("📦 Trash folder left unchanged.")
            
            print("\n✅ Gmail cleanup completed successfully.\n")
            print("-" * 50)
        
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please check your credentials and internet connection.")
