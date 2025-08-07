# Gmail Cleanup Tool - Setup Guide

## For End Users (Easy Setup)

If you received this tool from someone else, you should be able to run it directly:

```bash
python main.py
```

The tool will guide you through authentication. No Google Cloud setup required!

## For Developers (One-time Setup)

To make this tool work for anyone, you need to set up OAuth credentials once:

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (e.g., "Gmail Cleanup Tool")
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### Step 2: Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop application"
4. Name it "Gmail Cleanup Tool"
5. Download the JSON file

### Step 3: Configure the App

Option A: Replace the placeholder values in `main.py`:
```python
DEFAULT_CLIENT_CONFIG = {
    "installed": {
        "client_id": "YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com",
        "client_secret": "YOUR_ACTUAL_CLIENT_SECRET",
        # ... other fields stay the same
    }
}
```

Option B: Include the downloaded JSON as `credentials.json` in the project folder.

### Step 4: Distribute

Users can now run the tool without any Google Cloud setup. They'll just need to:
1. Run `python main.py`
2. Authorize the app in their browser
3. Use the tool normally

## Security Notes

- OAuth credentials in the code are safe for public distribution
- Users' Gmail access tokens are stored locally in `token.json`
- The app only requests Gmail access (no other Google services)
- Users can revoke access anytime in their Google Account settings

## Alternative: Package as Executable

To make it even easier for non-technical users:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --name gmail-cleanup main.py
```

This creates a single executable file that users can run without Python installed.
