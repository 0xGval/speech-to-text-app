"""
Text processor module.
Cleans and corrects transcribed text.
"""

import re
from typing import Optional


class TextProcessor:
    """Processes and cleans transcribed text."""

    def __init__(self, corrections: Optional[list] = None):
        """
        Initialize processor.

        Args:
            corrections: List of [pattern, replacement] pairs
        """
        self.corrections = corrections or []

    def process(self, text: str) -> str:
        """
        Process text: apply corrections and clean up.

        Args:
            text: Raw transcribed text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        result = text

        # Apply custom corrections
        for pattern, replacement in self.corrections:
            result = result.replace(pattern, replacement)

        # Clean up extra whitespace
        result = re.sub(r"\s+", " ", result)
        result = result.strip()

        return result

    def format_for_terminal(self, text: str) -> str:
        """
        Format text for terminal input.
        Removes problematic characters.
        """
        # Remove characters that might cause issues
        result = text.replace("\n", " ")
        result = result.replace("\r", "")
        result = result.replace("\t", " ")

        # Clean up
        result = re.sub(r"\s+", " ", result).strip()

        return result
