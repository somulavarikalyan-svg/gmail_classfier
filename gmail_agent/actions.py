"""
Action Handler.
Executes actions (Label, Archive) on emails and creates filters for trusted senders.
Handles Dry-Run logic to prevent unwanted changes during testing.
"""
from typing import Any
from .logger import logger
from .storage import MARKETING_TYPES

class ActionHandler:
    """
    Orchestrates Gmail actions based on decisions.
    """
    def __init__(self, gmail_service: Any, dry_run: bool = False) -> None:
        self.gmail = gmail_service
        self.dry_run = dry_run

    def execute_action(self, message_id: str, action: str, classification: str) -> None:
        """
        Execute the determined action on a message.
        
        Args:
            message_id: The ID of the message.
            action: The action to take ('ARCHIVE', 'REVIEW', 'SKIP').
            classification: The classification category.
        """
        label_name = f"AUTO/{classification.capitalize()}"
        
        if action == "SKIP":
            logger.info(f"Action: SKIP for {message_id}")
            return

        if self.dry_run:
            logger.info(f"[DRY RUN] Would apply label {label_name} to {message_id}")
            if action == "ARCHIVE":
                logger.info(f"[DRY RUN] Would archive {message_id}")
            return

        # Apply Label
        self.gmail.add_label(message_id, label_name)
        
        # Archive if needed
        if action == "ARCHIVE":
            self.gmail.archive_message(message_id)

    def create_filter_if_trusted(self, sender_email: str, classification: str, is_trusted: bool) -> None:
        """
        Create a filter if the sender is trusted and it's a marketing category.
        
        Args:
            sender_email: The sender's email address.
            classification: The classification category.
            is_trusted: Boolean indicating if the sender is trusted.
        """
        if not is_trusted:
            return

        # Only create filters for marketing categories
        if classification not in MARKETING_TYPES:
            return

        label_name = f"AUTO/{classification.capitalize()}"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create filter for {sender_email} -> {label_name}")
            return

        logger.info(f"Creating filter for trusted sender {sender_email}")
        self.gmail.create_filter(sender_email, label_name)
