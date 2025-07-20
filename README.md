# Gmail Cleanup Automation: Delete Promotions, Social & Updates Automatically
This guide helps you automate deleting Gmail messages from the Promotions, Social, and Updates categories using Python and the Gmail API.

🎯 Objective
Automatically search and delete all emails in Gmail tabs:
- Promotions
- Social
- Updates

🛠️ Prerequisites
- A Gmail (Google) account
- Python 3.6 or later
- A Google Cloud Project with Gmail API enabled

🚀 Step-by-Step Setup

✅ Step 1: Create a Google Cloud Project.
1. Visit the Google Cloud Console.
2. Click "New Project", name your project, and create it
3. After creation:

  - Go to APIs & Services > Library.
  - Search "Gmail API", click it, and click Enable.

✅ Step 2: Configure OAuth Consent Screen

1. Go to OAuth consent screen.
2. Choose External.
3. Fill in:
  - App Name: e.g., Gmail Cleanup Script.
  - User Support Email: your Gmail.
  - Developer Contact: your Gmail.
4. Skip scopes (for personal use).
5. Add your Gmail to Test Users.
6. Save and go back to Credentials page.

✅ Step 3: Create OAuth Credentials
1. Go to APIs & Services > Credentials
2. Click "Create Credentials > OAuth Client ID"
3. Choose:
  - Application Type: Desktop app.
  - Name: e.g., gmail-script.
4. Click Create
5. Immediately download the JSON file
   - Rename to: credentials.json.
   - Place it in the same directory as your script.
⚠️ If you close the dialog without downloading, you will have to delete and recreate it!

✅ Step 4: Install Python Libraries

- Command: python -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

✅ Step 5: Run the Script
- Command:python delete_gmail_categories.py.
- On the first run, a browser will open → log in → allow access.
- A token.json file will be generated for future runs.

❗ Common Issues and Fixes
  1. Error 403: access_denied
  - Reason: Your Gmail is not added as a Test User.
  - Fix:
      - Go to OAuth Consent Screen settings.
      - Add your Gmail as a Test User.

2. Missing credentials.json
 - You must download it right after creating the OAuth client.
 - If missed:
           - Delete the client from credentials list.
           - Create a new one and download again.

3. pip command not working
- Try using:
         - Command: python -m pip install ...

📂 Suggested Folder Structure
 gmail_cleaner/
├── delete_gmail_categories.py
├── credentials.json      # Downloaded from Google
└── token.json            # Auto-created on first run

✅ You're Done!
Feel free to star this repo ⭐, suggest improvements, or reach out if you need help.

Automation saves time and peace of mind 🕊️ — Clean inbox, clear mind.

Demo✅
<img width="1363" height="713" alt="image" src="https://github.com/user-attachments/assets/29c31c66-67cd-4f6b-9444-cf4210006ddc" />

<img width="1004" height="268" alt="image" src="https://github.com/user-attachments/assets/1be49c0b-379f-4abc-91fd-2f5734732c95" />

