from typing import List, Dict, Any, Optional
from .logger import logger

class MockGmailService:
    """
    A mock version of GmailService that returns fake data for testing purposes.
    Used when running with --mock flag or when credentials are missing.
    """
    def __init__(self):
        logger.info("Initialized MockGmailService")

    def list_messages(self, query: str = "is:unread", max_results: int = 10) -> List[Dict[str, str]]:
        """Returns a list of dummy message IDs."""
        logger.info(f"[MOCK] Listing messages with query='{query}' limit={max_results}")
        # Return some fake message IDs
        return [
            {'id': 'mock_msg_1', 'threadId': 'mock_thread_1'},
            {'id': 'mock_msg_2', 'threadId': 'mock_thread_2'},
            {'id': 'mock_msg_3', 'threadId': 'mock_thread_3'},
            {'id': 'mock_msg_4', 'threadId': 'mock_thread_4'},
            {'id': 'mock_msg_5', 'threadId': 'mock_thread_5'},
        ]

    def get_message_details(self, msg_id: str) -> Optional[Dict[str, Any]]:
        """Returns fake details for a message ID."""
        logger.info(f"[MOCK] Getting details for {msg_id}")
        
        # Define some fake scenarios
        scenarios = {
            'mock_msg_1': {
                'subject': 'Weekly Newsletter',
                'sender': 'Newsletter <news@marketing.com>',
                'email_address': 'news@marketing.com',
                'snippet': 'Here are the top stories for this week...'
            },
            'mock_msg_2': {
                'subject': 'Your Invoice',
                'sender': 'Billing <billing@service.com>',
                'email_address': 'billing@service.com',
                'snippet': 'Please find attached your invoice for...'
            },
            'mock_msg_3': {
                'subject': 'Limited Time Offer',
                'sender': 'Promo <promo@shop.com>',
                'email_address': 'promo@shop.com',
                'snippet': '50% off everything this weekend only!'
            },
            'mock_msg_4': {
                'subject': 'Security Alert',
                'sender': 'Google <no-reply@accounts.google.com>',
                'email_address': 'no-reply@accounts.google.com',
                'snippet': 'New sign-in detected on your account.'
            },
            'mock_msg_5': {
                'subject': 'Meeting Update',
                'sender': 'John Doe <john.doe@company.com>',
                'email_address': 'john.doe@company.com',
                'snippet': 'Can we reschedule our sync to 3 PM?'
            }
        }
        
        data = scenarios.get(msg_id, {
            'subject': 'Unknown Subject',
            'sender': 'Unknown <unknown@example.com>',
            'email_address': 'unknown@example.com',
            'snippet': 'Lorem ipsum...'
        })
        
        return {
            'id': msg_id,
            'subject': data['subject'],
            'sender': data['sender'],
            'email_address': data['email_address'],
            'snippet': data['snippet'],
            'threadId': f"thread_{msg_id}"
        }

    def add_label(self, msg_id: str, label_name: str) -> None:
        logger.info(f"[MOCK] Added label '{label_name}' to {msg_id}")

    def archive_message(self, msg_id: str) -> None:
        logger.info(f"[MOCK] Archived message {msg_id}")

    def create_filter(self, sender_email: str, label_name: str) -> None:
        logger.info(f"[MOCK] Created filter: From {sender_email} -> Label {label_name}")
