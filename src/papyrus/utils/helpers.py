"""Utility functions for resource management and HTML processing."""

import sys
import os
from bs4 import BeautifulSoup


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller/py2app.

    Args:
        relative_path: Relative path to the resource file

    Returns:
        Absolute path to the resource
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller
        base_path = sys._MEIPASS
    elif "RESOURCEPATH" in os.environ:
        # py2app
        base_path = os.environ["RESOURCEPATH"]
    else:
        # Development: helpers.py is in src/papyrus/utils/
        # We want the base to be root (parent of src)
        # src/papyrus/utils -> src/papyrus -> src -> root
        base_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )

    return os.path.join(base_path, relative_path)


def clean_pasted_html(text: str) -> str:
    """Clean and format pasted HTML using BeautifulSoup.

    This function parses the input HTML, fixes malformed tags, and returns
    a pretty-printed version. If the input is not valid HTML, it returns
    the original text.

    Args:
        text: HTML text to clean

    Returns:
        Cleaned and formatted HTML text
    """
    if not text or not text.strip():
        return text

    try:
        # Use html.parser as it's built-in, though lxml is faster if available
        soup = BeautifulSoup(text, "html.parser")

        # If it's just a fragment, we might want to keep it as a fragment
        # But for now, let's just pretty print whatever we get
        return soup.prettify()
    except Exception:
        # Fallback to original text if parsing fails
        return text
