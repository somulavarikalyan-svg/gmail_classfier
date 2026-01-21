from typing import Optional
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from .config import CREDENTIALS_FILE, TOKEN_FILE, SCOPES
from .logger import logger

def authenticate_gmail() -> Optional[Credentials]:
    """
    Authenticates the user with Gmail API using OAuth2.
    
    Returns:
        Credentials object if successful, None otherwise.
        
    Raises:
        FileNotFoundError: If credentials.json is missing.
    """
    creds: Optional[Credentials] = None
    
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            logger.error(f"Error loading token file: {e}")
            creds = None
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Refreshing expired token...")
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing token: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                logger.error(f"Credentials file not found at {CREDENTIALS_FILE}")
                raise FileNotFoundError(f"Please place credentials.json at {CREDENTIALS_FILE}")
            
            try:
                logger.info("Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logger.error(f"OAuth flow failed: {e}")
                raise

        # Save the credentials for the next run
        try:
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            logger.error(f"Failed to save token file: {e}")
            
    return creds
