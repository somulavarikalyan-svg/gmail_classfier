"""
LLM Service Wrapper.
Handles interactions with the local Ollama instance for email classification.
"""
import requests
import json
from typing import Tuple, Dict, Any
from .config import OLLAMA_URL, OLLAMA_MODEL
from .logger import logger

class LLMService:
    """
    Service for interacting with the local LLM (Ollama).
    """
    def __init__(self) -> None:
        self.url: str = OLLAMA_URL
        self.model: str = OLLAMA_MODEL

    def classify_email(self, subject: str, snippet: str, sender: str) -> Tuple[str, float]:
        """
        Classify email using Ollama.
        
        Args:
            subject: The email subject line.
            snippet: A short snippet of the email body.
            sender: The sender's name and/or email.
            
        Returns:
            A tuple containing:
            - classification (str): The category (e.g., 'NEWSLETTER', 'IMPORTANT').
            - confidence (float): A score between 0.0 and 1.0.
        """
        prompt = f"""
        You are an email classifier. Classify the following email into one of these categories:
        - NEWSLETTER
        - PROMOTION
        - OUTREACH
        - COURSE
        - IMPORTANT (Personal, Work, Bills, Legal, Medical, etc.)

        Sender: {sender}
        Subject: {subject}
        Snippet: {snippet}

        Respond with JSON only:
        {{
            "classification": "CATEGORY",
            "confidence": 0.0 to 1.0
        }}
        """

        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }

        try:
            response = requests.post(self.url, json=payload, timeout=30) # Added timeout
            response.raise_for_status()
            result = response.json()
            
            # Parse the 'response' field which contains the actual generation
            # Ollama 'json' format mode usually guarantees valid JSON in 'response'
            generation = json.loads(result['response'])
            
            classification = generation.get('classification', 'IMPORTANT').upper()
            confidence = float(generation.get('confidence', 0.0))
            
            return classification, confidence

        except requests.exceptions.RequestException as e:
            logger.error(f"LLM connection failed: {e}")
            return "IMPORTANT", 0.0
        except json.JSONDecodeError as e:
            logger.error(f"LLM returned invalid JSON: {e}")
            return "IMPORTANT", 0.0
        except Exception as e:
            logger.error(f"LLM unexpected error: {e}")
            return "IMPORTANT", 0.0
