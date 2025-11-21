"""Utility functions for resource management and HTML processing."""
import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller.

    Args:
        relative_path: Relative path to the resource file

    Returns:
        Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # pylint: disable=protected-access,no-member
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def clean_pasted_html(text: str) -> str:
    """Clean pasted HTML by removing content before DOCTYPE declaration.

    Args:
        text: HTML text to clean

    Returns:
        Cleaned HTML text
    """
    lower_text = text.lower()
    doctype_pos = lower_text.find('<!doctype html>')
    if doctype_pos > 0:
        return text[lower_text.find('<!doctype html>'):]
    return text
