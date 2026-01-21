"""
Email Classifier Logic.
Determines safety of emails and decides on actions based on LLM classification and confidence scores.
"""
from typing import Literal
from .config import (
    PROTECTED_DOMAINS, PROTECTED_KEYWORDS,
    CONFIDENCE_ARCHIVE, CONFIDENCE_REVIEW
)
from .logger import logger

# Define a type alias for Actions
ActionType = Literal["ARCHIVE", "REVIEW", "SKIP"]

class Classifier:
    """
    Encapsulates logic for safety checks and action determination.
    """
    def __init__(self) -> None:
        pass

    def is_safe_sender(self, sender_email: str) -> bool:
        """
        Check if sender is in protected domains.
        
        Args:
            sender_email: The sender's email address.
            
        Returns:
            True if the sender is protected (should NOT be touched), False otherwise.
        """
        if not sender_email or '@' not in sender_email:
            return False
            
        domain = sender_email.split('@')[-1].lower()
        for protected in PROTECTED_DOMAINS:
            if protected in domain:
                logger.info(f"Safety Rule: Protected domain {domain} detected for {sender_email}")
                return True
        return False

    def is_safe_content(self, subject: str, snippet: str) -> bool:
        """
        Check if content contains protected keywords.
        
        Args:
            subject: Email subject.
            snippet: Email snippet.
            
        Returns:
            True if content is protected (should NOT be touched), False otherwise.
        """
        text = (subject + " " + snippet).lower()
        for keyword in PROTECTED_KEYWORDS:
            if keyword in text:
                logger.info(f"Safety Rule: Protected keyword '{keyword}' detected.")
                return True
        return False

    def determine_action(self, classification: str, confidence: float) -> ActionType:
        """
        Determine action based on classification and confidence.
        
        Args:
            classification: The category returned by LLM.
            confidence: The confidence score (0.0 - 1.0).
            
        Returns:
            'ARCHIVE', 'REVIEW', or 'SKIP'.
        """
        if classification == "IMPORTANT":
            return "SKIP"

        if confidence >= CONFIDENCE_ARCHIVE:
            return "ARCHIVE"
        elif confidence >= CONFIDENCE_REVIEW:
            return "REVIEW"
        else:
            return "SKIP"
