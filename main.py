"""
Main Entry Point for the Gmail Cleanup Agent.
Orchestrates the entire workflow:
1. Initialize services (Gmail, LLM, Storage).
2. Fetch recent emails.
3. Apply safety checks.
4. Classify emails using LLM.
5. Update sender memory.
6. Determine and execute actions (Label, Archive).
7. Create filters for trusted senders.
"""
import argparse
import sys
from typing import Optional, Dict, Any

from gmail_agent.gmail_service import GmailService
from gmail_agent.mock_service import MockGmailService
from gmail_agent.llm_service import LLMService
from gmail_agent.storage import Storage
from gmail_agent.classifier import Classifier
from gmail_agent.actions import ActionHandler
from gmail_agent.logger import logger

def main() -> None:
    """
    Main execution function.
    Parses CLI arguments and runs the agent loop.
    """
    parser = argparse.ArgumentParser(description="Gmail Cleanup Agent")
    parser.add_argument('--dry-run', action='store_true', help="Run without making changes")
    parser.add_argument('--mock', action='store_true', help="Run with mock data (no Gmail connection)")
    parser.add_argument('--limit', type=int, default=10, help="Number of emails to process")
    args = parser.parse_args()

    logger.info(f"Starting Gmail Agent (Dry Run: {args.dry_run}, Mock: {args.mock})")

    try:
        # Initialize Services
        gmail: Any  # Union[GmailService, MockGmailService]
        if args.mock:
            gmail = MockGmailService()
        else:
            gmail = GmailService()
            
        llm = LLMService()
        storage = Storage()
        classifier = Classifier()
        actions = ActionHandler(gmail, dry_run=args.dry_run)

        # List Messages
        messages = gmail.list_messages(max_results=args.limit)
        logger.info(f"Found {len(messages)} messages to process.")

        for msg in messages:
            details = gmail.get_message_details(msg['id'])
            if not details:
                continue

            sender = details['sender']
            email_address = details['email_address']
            subject = details['subject']
            snippet = details['snippet']

            logger.info(f"Processing: {subject} | From: {sender}")

            # 1. Safety Checks (Pre-LLM)
            if classifier.is_safe_sender(email_address):
                logger.info(f"Skipping protected sender: {email_address}")
                continue
            
            if classifier.is_safe_content(subject, snippet):
                logger.info("Skipping protected content.")
                continue

            # 2. Classify
            classification, confidence = llm.classify_email(subject, snippet, sender)
            logger.info(f"Classified as {classification} ({confidence:.2f})")

            # 3. Update Memory
            just_became_trusted = storage.update_sender(email_address, classification)
            is_trusted = storage.is_trusted(email_address)

            # 4. Determine Action
            action = classifier.determine_action(classification, confidence)
            
            # 5. Execute Action
            actions.execute_action(details['id'], action, classification)

            # 6. Filter Automation
            if just_became_trusted:
                logger.info(f"Sender {email_address} just became trusted!")
                actions.create_filter_if_trusted(email_address, classification, is_trusted)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

    logger.info("Run complete.")

if __name__ == "__main__":
    main()
