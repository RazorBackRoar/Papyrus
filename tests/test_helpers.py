"""Logic tests for Papyrus helpers and sanitization."""

from papyrus.utils import helpers


def test_clean_pasted_html_handles_empty_and_invalid():
    """Ensure cleaning handles empty input and fixes malformed HTML."""
    assert helpers.clean_pasted_html("") == ""
    bad = "<div><p>unclosed"
    cleaned = helpers.clean_pasted_html(bad)
    assert "<div>" in cleaned and "</div>" in cleaned


def test_sanitize_for_pdf_copy_removes_control_chars():
    """Ensure sanitize_for_pdf_copy removes zero-width/soft hyphen chars."""
    from papyrus.core.app import HTMLConverterApp  # pylint: disable=import-outside-toplevel

    app = HTMLConverterApp()
    raw = "Hello\u200bWorld\u00ad"
    sanitized = app.sanitize_for_pdf_copy(raw)
    assert "\u200b" not in sanitized
    assert "\u00ad" not in sanitized
