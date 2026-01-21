import unittest
from unittest.mock import MagicMock
from gmail_agent.storage import Storage
from gmail_agent.classifier import Classifier
from gmail_agent.actions import ActionHandler
from gmail_agent.config import CONFIDENCE_ARCHIVE, CONFIDENCE_REVIEW

class TestGmailAgent(unittest.TestCase):
    def setUp(self):
        self.storage = Storage()
        # Reset storage data for testing
        self.storage.data = {}
        self.classifier = Classifier()
        self.mock_gmail = MagicMock()
        self.actions = ActionHandler(self.mock_gmail, dry_run=False)

    def test_safety_rules(self):
        # Protected Domain
        self.assertTrue(self.classifier.is_safe_sender("support@google.com"))
        self.assertFalse(self.classifier.is_safe_sender("newsletter@marketing.com"))
        
        # Protected Keyword
        self.assertTrue(self.classifier.is_safe_content("Your Invoice", "Please find attached"))
        self.assertFalse(self.classifier.is_safe_content("Weekly Newsletter", "Check this out"))

    def test_confidence_routing(self):
        # High confidence -> Archive
        self.assertEqual(self.classifier.determine_action("NEWSLETTER", 0.85), "ARCHIVE")
        # Medium confidence -> Review
        self.assertEqual(self.classifier.determine_action("NEWSLETTER", 0.60), "REVIEW")
        # Low confidence -> Skip
        self.assertEqual(self.classifier.determine_action("NEWSLETTER", 0.40), "SKIP")
        # Important -> Skip
        self.assertEqual(self.classifier.determine_action("IMPORTANT", 0.99), "SKIP")

    def test_sender_memory_and_filter_creation(self):
        sender = "promo@brand.com"
        
        # 1st time
        trusted = self.storage.update_sender(sender, "PROMOTION")
        self.assertFalse(trusted)
        self.assertFalse(self.storage.is_trusted(sender))
        
        # 2nd time
        trusted = self.storage.update_sender(sender, "PROMOTION")
        self.assertFalse(trusted)
        
        # 3rd time -> Should become trusted
        trusted = self.storage.update_sender(sender, "PROMOTION")
        self.assertTrue(trusted)
        self.assertTrue(self.storage.is_trusted(sender))
        
        # Check if filter creation is triggered
        self.actions.create_filter_if_trusted(sender, "PROMOTION", True)
        self.mock_gmail.create_filter.assert_called_with(sender, "AUTO/Promotion")

    def test_action_execution(self):
        msg_id = "123"
        
        # Archive Action
        self.actions.execute_action(msg_id, "ARCHIVE", "NEWSLETTER")
        self.mock_gmail.add_label.assert_called_with(msg_id, "AUTO/Newsletter")
        self.mock_gmail.archive_message.assert_called_with(msg_id)
        
        # Review Action
        self.mock_gmail.reset_mock()
        self.actions.execute_action(msg_id, "REVIEW", "NEWSLETTER")
        self.mock_gmail.add_label.assert_called_with(msg_id, "AUTO/Newsletter")
        self.mock_gmail.archive_message.assert_not_called()

if __name__ == '__main__':
    unittest.main()
