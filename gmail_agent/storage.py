"""
Persistent storage management for the Gmail Cleanup Agent.
Handles reading/writing sender data to JSON and tracking classification history.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Final
from .config import SENDERS_FILE, TRUSTED_SENDER_THRESHOLD
from .logger import logger

MARKETING_TYPES: Final[List[str]] = ["NEWSLETTER", "PROMOTION", "COURSE", "OUTREACH"]

class Storage:
    """
    Manages persistent storage for sender memory.
    Data is saved to a JSON file defined in config.SENDERS_FILE.
    """
    
    def __init__(self) -> None:
        self.file_path: str = SENDERS_FILE
        self.data: Dict[str, Any] = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Loads sender data from JSON file. Returns empty dict if file doesn't exist or is corrupt."""
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load storage from {self.file_path}: {e}")
            return {}

    def _save_data(self) -> None:
        """Saves current memory to JSON file."""
        try:
            # Atomic write pattern could be better, but simple write is sufficient for now
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)
        except IOError as e:
            logger.error(f"Failed to save storage to {self.file_path}: {e}")

    def update_sender(self, sender_email: str, classification: str) -> bool:
        """
        Updates the classification count for a sender.
        
        Args:
            sender_email: The email address of the sender.
            classification: The classification category (e.g., 'NEWSLETTER').
            
        Returns:
            bool: True if the sender *just* became a trusted marketing source in this update.
        """
        if sender_email not in self.data:
            self.data[sender_email] = {
                "domain": sender_email.split('@')[-1].lower(),
                "classifications": {},
                "last_seen": "",
                "trusted_marketing_source": False
            }
        
        entry = self.data[sender_email]
        entry["last_seen"] = datetime.now().isoformat()
        
        # Update classification counts
        current_count = entry["classifications"].get(classification, 0)
        entry["classifications"][classification] = current_count + 1
        
        # Check for trusted status upgrade
        was_trusted = entry["trusted_marketing_source"]
        
        if classification in MARKETING_TYPES:
            total_marketing_count = sum(entry["classifications"].get(t, 0) for t in MARKETING_TYPES)
            if total_marketing_count >= TRUSTED_SENDER_THRESHOLD:
                entry["trusted_marketing_source"] = True
        
        self._save_data()
        
        # Return True only if it JUST became trusted
        return entry["trusted_marketing_source"] and not was_trusted

    def is_trusted(self, sender_email: str) -> bool:
        """Checks if a sender is a trusted marketing source."""
        return self.data.get(sender_email, {}).get("trusted_marketing_source", False)

    def get_sender_data(self, sender_email: str) -> Optional[Dict[str, Any]]:
        """Retrieves raw data for a specific sender."""
        return self.data.get(sender_email)
