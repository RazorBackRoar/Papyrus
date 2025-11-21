import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def clean_pasted_html(text: str) -> str:
    lower_text = text.lower()
    doctype_pos = lower_text.find('<!doctype html>')
    if doctype_pos > 0:
        return text[lower_text.find('<!doctype html>'):]
    return text
