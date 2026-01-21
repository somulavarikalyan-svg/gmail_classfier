"""
Gmail API Service Wrapper.
Handles all interactions with the Google Gmail API, including listing messages,
retrieving details, modifying labels, and creating filters.
"""
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from email.utils import parseaddr
from .auth import authenticate_gmail
from .logger import logger
from .config import PROTECTED_DOMAINS

class GmailService:
    """
    Wrapper class for the Gmail API.
    """
    def __init__(self) -> None:
        self.creds = authenticate_gmail()
        if not self.creds:
            raise RuntimeError("Failed to authenticate with Gmail.")
        self.service = build('gmail', 'v1', credentials=self.creds)

    def list_messages(self, query: str = "is:unread", max_results: int = 10) -> List[Dict[str, str]]:
        """
        List messages matching the query.
        
        Args:
            query: Gmail search query (default: "is:unread").
            max_results: Maximum number of messages to return.
            
        Returns:
            List of message dictionaries containing 'id' and 'threadId'.
        """
        try:
            results = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            messages = results.get('messages', [])
            return messages
        except Exception as e:
            logger.error(f"An error occurred listing messages: {e}")
            return []

    def get_message_details(self, msg_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full details of a message.
        
        Args:
            msg_id: The ID of the message to retrieve.
            
        Returns:
            Dictionary with subject, sender, email_address, snippet, etc., or None if failed.
        """
        try:
            message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            headers = message['payload']['headers']
            
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
            snippet = message.get('snippet', '')
            
            # Extract email address from sender
            _, email_address = parseaddr(sender)
            
            return {
                'id': msg_id,
                'subject': subject,
                'sender': sender,
                'email_address': email_address,
                'snippet': snippet,
                'threadId': message['threadId']
            }
        except Exception as e:
            logger.error(f"An error occurred getting message details for {msg_id}: {e}")
            return None

    def add_label(self, msg_id: str, label_name: str) -> None:
        """
        Add a label to a message. Creates the label if it doesn't exist.
        
        Args:
            msg_id: The ID of the message.
            label_name: The name of the label to add.
        """
        try:
            label_id = self._get_or_create_label_id(label_name)
            
            body = {
                'addLabelIds': [label_id],
                'removeLabelIds': []
            }
            self.service.users().messages().modify(userId='me', id=msg_id, body=body).execute()
            logger.info(f"Added label {label_name} to message {msg_id}")
        except Exception as e:
            logger.error(f"Failed to add label {label_name} to {msg_id}: {e}")

    def archive_message(self, msg_id: str) -> None:
        """
        Archive a message by removing the 'INBOX' label.
        
        Args:
            msg_id: The ID of the message to archive.
        """
        try:
            body = {
                'removeLabelIds': ['INBOX']
            }
            self.service.users().messages().modify(userId='me', id=msg_id, body=body).execute()
            logger.info(f"Archived message {msg_id}")
        except Exception as e:
            logger.error(f"Failed to archive message {msg_id}: {e}")

    def _get_or_create_label_id(self, label_name: str) -> str:
        """
        Helper to get label ID by name, or create it if missing.
        
        Args:
            label_name: The display name of the label.
            
        Returns:
            The Label ID string.
        """
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            for label in labels:
                if label['name'].lower() == label_name.lower():
                    return label['id']
            
            # Create if not found
            label_object = {'name': label_name}
            created_label = self.service.users().labels().create(userId='me', body=label_object).execute()
            return created_label['id']
        except Exception as e:
            logger.error(f"Error getting/creating label {label_name}: {e}")
            raise

    def create_filter(self, sender_email: str, label_name: str) -> None:
        """
        Create a filter for a specific sender to apply a label and archive.
        
        Args:
            sender_email: The email address to filter.
            label_name: The label to apply.
        """
        # Safety check
        domain = sender_email.split('@')[-1]
        if any(protected in domain for protected in PROTECTED_DOMAINS):
            logger.warning(f"Attempted to create filter for protected domain {domain}. Aborted.")
            return

        try:
            label_id = self._get_or_create_label_id(label_name)
            
            filter_content = {
                'criteria': {
                    'from': sender_email
                },
                'action': {
                    'addLabelIds': [label_id],
                    'removeLabelIds': ['INBOX']
                }
            }
            self.service.users().settings().filters().create(userId='me', body=filter_content).execute()
            logger.info(f"Created filter for {sender_email} -> {label_name}")
        except Exception as e:
            logger.error(f"Failed to create filter for {sender_email}: {e}")

