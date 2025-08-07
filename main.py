import os
import time
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://mail.google.com/']

def gmail_login():
    """Simplified Gmail authentication that works for any user"""
    creds = None
    
    # Check if user has existing token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("🔄 Refreshing authentication token...")
                creds.refresh(Request())
            except Exception as e:
                print(f"⚠️ Token refresh failed: {e}")
                print("Starting new authentication process...")
                os.remove('token.json')
                return gmail_login()
        else:
            print("\n🔐 Gmail Authentication Required")
            print("=" * 40)
            print("This app needs permission to access your Gmail account.")
            print("A browser window will open for you to sign in and authorize access.")
            print("Your credentials will be saved locally for future use.\n")
            
            # Use embedded client config or fallback to credentials.json
            try:
                if os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                else:
                    pass
                    # Use the pre-configured client config
                    # flow = InstalledAppFlow.from_client_config(DEFAULT_CLIENT_CONFIG, SCOPES)
                
                print("🌐 Opening browser for authentication...")
                creds = flow.run_local_server(port=0)
                print("✅ Authentication successful!")
                
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                print("\n💡 Setup Instructions:")
                print("1. This app needs to be configured with OAuth credentials")
                print("2. Contact the developer for setup assistance")
                print("3. Or create your own Google Cloud project:")
                print("   - Go to https://console.cloud.google.com")
                print("   - Create a new project")
                print("   - Enable Gmail API")
                print("   - Create OAuth 2.0 credentials")
                print("   - Download as 'credentials.json'")
                return None
        
        # Save credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("💾 Credentials saved for future use.")

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

def delete_emails_by_category(service, category, custom_query=None):
    print(f"\n🔍 Checking for emails in category: {category}...")
    try:
        # Use custom query if provided, otherwise use predefined queries
        if custom_query:
            query = custom_query
        elif category == 'inbox-unread':
            query = "is:unread"
        else:
            query = f"category:{category}"
        
        print(f"📝 Using query: {query}")
        msg_ids = fetch_all_message_ids(service, query)

        if not msg_ids:
            print(f"✅ No emails found for query: {query}. Moving to next category.")
            return

        total_deleted = 0
        for i in range(0, len(msg_ids), 1000):
            batch = msg_ids[i:i + 1000]
            service.users().messages().batchDelete(userId='me', body={'ids': batch}).execute()
            total_deleted += len(batch)

        print(f"🗑️ {total_deleted} emails permanently deleted for query: {query}")

    except HttpError as error:
        print(f"❌ Error while deleting emails: {error}")

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
    print("1. Inbox Unread")
    print("2. Primary")
    print("3. Promotions")
    print("4. Updates") 
    print("5. Social")
    print("6. Custom Query")
    print("7. All categories")
    print("8. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-8): ").strip()
            if choice == '1':
                return ['inbox-unread'], None
            elif choice == '2':
                return ['primary'], None
            elif choice == '3':
                return ['promotions'], None
            elif choice == '4':
                return ['updates'], None
            elif choice == '5':
                return ['social'], None
            elif choice == '6':
                return get_custom_query()
            elif choice == '7':
                return ['inbox-unread', 'primary', 'promotions', 'updates', 'social'], None
            elif choice == '8':
                print("👋 Goodbye!")
                return None, None
            else:
                print("❌ Invalid choice. Please enter a number between 1-8.")
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user.")
            return None, None

def get_custom_query():
    """Get custom Gmail search query from user"""
    print("\n🔍 Custom Query Mode")
    print("=" * 30)
    print("Examples of Gmail search queries:")
    print("  • label:monster")
    print("  • from:newsletter@example.com")
    print("  • subject:unsubscribe")
    print("  • older_than:1y")
    print("  • has:attachment larger:10M")
    print("  • is:unread from:notifications")
    print("\n💡 Tip: You can combine multiple terms, e.g., 'label:monster is:unread'")
    
    while True:
        try:
            query = input("\nEnter your Gmail search query: ").strip()
            if not query:
                print("❌ Query cannot be empty. Please enter a valid Gmail search query.")
                continue
            
            # Confirm the query with user
            print(f"\n📝 Your query: {query}")
            confirm = input("Is this correct? (y/n): ").strip().lower()
            
            if confirm in ['y', 'yes']:
                return ['custom'], query
            elif confirm in ['n', 'no']:
                continue
            else:
                print("❌ Please enter 'y' for yes or 'n' for no.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user.")
            return None, None

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
            categories, custom_query = get_user_category_choice()
            if not categories:
                break
            
            # Process selected categories
            for category in categories:
                if category == 'custom' and custom_query:
                    delete_emails_by_category(service, category, custom_query)
                else:
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
