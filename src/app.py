import os
import json
import tempfile
import subprocess
import webbrowser
import platform
from datetime import datetime
from functools import partial

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QTabWidget,
    QCheckBox,
    QMessageBox,
    QFrame,
    QLineEdit,
    QSpinBox,
    QScrollArea,
    QDialog,
    QSizePolicy,
    QApplication,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPalette, QColor, QKeySequence, QShortcut

from utils.helpers import resource_path
from ui.editor import PagedTextEdit
from ui.highlighter import HTMLSyntaxHighlighter


class HTMLConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.colors = {
            "dark_grey": "#1e1e1e",
            "deep_orange": "#FF5A09",
            "light_orange": "#EC7F37",
            "orange_yellow": "#BE4F0C",
            "bright_blue": "#2a9df4",
            "darker_grey": "#141414",
            "lighter_grey": "#2c2c2c",
            "white": "#FFFFFF",
            "text_bg": "#1e1e1e",
            "text_fg": "#f0f0f0",
        }
        self.init_ui()
        self.setup_shortcuts()
        self.history_entries: list[dict] = []
        self.MAX_HISTORY = 50
        self._init_history_storage()

    def init_ui(self):
        self.setWindowTitle("")
        self.setWindowIcon(QIcon(resource_path("assets/papyrus.icns")))
        self.setGeometry(100, 100, 1000, 800)
        self.center_on_screen()
        self.setMinimumSize(600, 500)
        self.setStyleSheet(
            f"""
            QMainWindow {{ background-color: {self.colors['dark_grey']}; }}
            QWidget {{ background-color: {self.colors['dark_grey']}; color: {self.colors['white']}; }}
            QTabWidget {{ background-color: {self.colors['darker_grey']}; border: none; }}
            QTabWidget::pane {{ border: none; background-color: {self.colors['darker_grey']}; border-radius: 8px; }}
            QTabBar::tab {{ background-color: {self.colors['lighter_grey']}; color: {self.colors['white']}; padding: 10px 20px; margin-right: 5px; border-top-left-radius: 8px; border-top-right-radius: 8px; font-size: 14px; font-weight: 500; }}
            QTabBar::tab:selected {{ background-color: {self.colors['darker_grey']}; color: {self.colors['light_orange']}; }}
            QTabBar::tab:hover {{ background-color: {self.colors['orange_yellow']}; }}
            QTextEdit {{ background-color: {self.colors['text_bg']}; color: {self.colors['text_fg']}; border: 1px solid {self.colors['deep_orange']}; border-radius: 8px; padding: 10px; font-family: 'Menlo', 'Consolas', 'Monaco', 'Courier New', monospace; font-size: 12px; selection-background-color: {self.colors['orange_yellow']}; selection-color: {self.colors['white']}; }}
            QTextEdit QScrollBar:vertical, QTextEdit QScrollBar:horizontal {{ background: {self.colors['darker_grey']}; }}
            QTextEdit * {{ background-color: {self.colors['text_bg']} !important; margin: 0px !important; padding: 0px !important; }}
            QPushButton {{ background-color: {self.colors['deep_orange']}; color: {self.colors['white']}; border: none; border-radius: 8px; padding: 12px 30px; font-size: 16px; font-weight: bold; min-width: 150px; }}
            QPushButton:hover {{ background-color: {self.colors['light_orange']}; }}
            QPushButton:pressed {{ background-color: {self.colors['orange_yellow']}; }}
            QPushButton#secondary {{ background-color: {self.colors['lighter_grey']}; }}
            QPushButton#secondary:hover {{ background-color: {self.colors['orange_yellow']}; }}
            QCheckBox {{ color: {self.colors['white']}; font-size: 12px; spacing: 10px; }}
            QCheckBox::indicator {{ width: 18px; height: 18px; border: 2px solid #000000; border-radius: 4px; background-color: {self.colors['lighter_grey']}; }}
            QCheckBox::indicator:checked {{ background-color: {self.colors['deep_orange']}; border-color: {self.colors['deep_orange']}; }}
            QLabel {{ color: {self.colors['white']}; }}
            QLabel#title {{ color: {self.colors['light_orange']}; font-size: 44px; font-weight: bold; }}
            QLabel#subtitle {{ color: {self.colors['white']}; font-size: 16px; }}
            QLabel#instruction {{ color: {self.colors['light_orange']}; font-size: 14px; }}
            QLabel#status {{ background-color: {self.colors['lighter_grey']}; color: {self.colors['white']}; padding: 8px 15px; border-radius: 4px; font-size: 11px; }}
            QLabel#shortcuts {{ color: {self.colors['orange_yellow']}; font-size: 10px; }}
            QLineEdit {{ background-color: {self.colors['text_bg']}; color: {self.colors['text_fg']}; border: 1px solid {self.colors['deep_orange']}; border-radius: 6px; padding: 6px 8px; selection-background-color: {self.colors['orange_yellow']}; selection-color: {self.colors['white']}; }}
            QLineEdit:focus {{ border: 1px solid {self.colors['deep_orange']}; }}
            QDialog {{ background-color: {self.colors['dark_grey']}; color: {self.colors['white']}; }}
            QScrollArea {{ background-color: {self.colors['dark_grey']}; border: none; }}
            QPushButton#historyItemButton {{ background-color: {self.colors['lighter_grey']}; color: {self.colors['deep_orange']}; border: none; border-radius: 10px; padding: 12px 16px; text-align: left; }}
            QPushButton#historyItemButton:hover {{ background-color: {self.colors['orange_yellow']}; color: {self.colors['white']}; }}
        """
        )
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        title_label = QLabel("Papyrus")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        subtitle_label = QLabel("Paste your HTML code and instantly preview or print")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)
        main_layout.addLayout(header_layout)
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        input_tab = QWidget()
        input_layout = QVBoxLayout(input_tab)
        input_layout.setContentsMargins(20, 20, 20, 20)
        instructions_label = QLabel("📝 Paste or type your HTML code below:")
        instructions_label.setObjectName("instruction")
        input_layout.addWidget(instructions_label)
        title_row = QHBoxLayout()
        title_row.addWidget(QLabel("Title:"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(
            "Give this conversion a title to save it in History"
        )
        title_row.addWidget(self.title_input)
        input_layout.addLayout(title_row)
        self.title_input.returnPressed.connect(self.save_title_to_history)
        self.text_editor = PagedTextEdit()
        self.text_editor.setMinimumHeight(400)
        self.text_editor.set_show_page_breaks(False)
        self.text_editor.setFrameShape(QFrame.Shape.NoFrame)
        palette = self.text_editor.palette()
        bg_color = QColor(self.colors["text_bg"])
        palette.setColor(QPalette.ColorRole.Base, bg_color)
        palette.setColor(QPalette.ColorRole.Window, bg_color)
        palette.setColor(QPalette.ColorRole.AlternateBase, bg_color)
        palette.setColor(QPalette.ColorRole.Button, bg_color)
        palette.setColor(QPalette.ColorRole.Mid, bg_color)
        palette.setColor(QPalette.ColorRole.Dark, bg_color)
        palette.setColor(QPalette.ColorRole.Shadow, bg_color)
        text_color = QColor(self.colors["text_fg"])
        palette.setColor(QPalette.ColorRole.Text, text_color)
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        palette.setColor(QPalette.ColorRole.ButtonText, text_color)
        self.text_editor.setPalette(palette)
        self.text_editor.viewport().setPalette(palette)
        self.text_editor.viewport().setAutoFillBackground(True)
        self.highlighter = HTMLSyntaxHighlighter(self.text_editor.document())
        self.text_editor.setPlaceholderText("Paste HTML here…")
        self.text_editor.document().setDocumentMargin(0)
        self.text_editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        input_layout.addWidget(self.text_editor)
        self.text_editor.setFocus()
        self.tab_widget.addTab(input_tab, "  HTML Input  ")
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.add_wrapper_checkbox = QCheckBox(
            "Add styling wrapper (adds beautiful dark theme if HTML lacks styles)"
        )
        self.add_wrapper_checkbox.setChecked(True)
        settings_layout.addWidget(self.add_wrapper_checkbox)
        # Auto-open checkbox removed
        self.add_print_bands_checkbox = QCheckBox(
            "Add repeated print bands (top & bottom) in print output"
        )
        self.add_print_bands_checkbox.setChecked(False)
        settings_layout.addWidget(self.add_print_bands_checkbox)
        # Enable copyable HTML code in PDF mode (escape and render as code)
        self.enable_pdf_copy_checkbox = QCheckBox(
            "Enable copyable HTML code in PDF (escape and render as code)"
        )
        self.enable_pdf_copy_checkbox.setChecked(False)
        settings_layout.addWidget(self.enable_pdf_copy_checkbox)
        band_text_row = QHBoxLayout()
        band_text_label = QLabel("Band text:")
        self.print_band_text = QLineEdit("Papyrus HTML Converter")
        self.print_band_text.setPlaceholderText(
            "Text to repeat across the top/bottom of each printed page"
        )
        band_text_row.addWidget(band_text_label)
        band_text_row.addWidget(self.print_band_text)
        settings_layout.addLayout(band_text_row)
        offset_row = QHBoxLayout()
        offset_row.addWidget(QLabel("Top offset (mm):"))
        self.top_offset_mm = QSpinBox()
        self.top_offset_mm.setRange(0, 50)
        self.top_offset_mm.setValue(12)
        offset_row.addWidget(self.top_offset_mm)
        offset_row.addWidget(QLabel("Bottom offset (mm):"))
        self.bottom_offset_mm = QSpinBox()
        self.bottom_offset_mm.setRange(0, 50)
        self.bottom_offset_mm.setValue(12)
        offset_row.addWidget(self.bottom_offset_mm)
        settings_layout.addLayout(offset_row)
        settings_layout.addStretch()
        self.tab_widget.addTab(settings_tab, "  Settings  ")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.safari_btn = QPushButton("🌐 Open in Browser")
        self.safari_btn.clicked.connect(self.open_in_browser)
        button_layout.addWidget(self.safari_btn)
        self.char_counter = QLabel("0")
        self.char_counter.setObjectName("status")
        button_layout.addWidget(self.char_counter)
        self.history_btn = QPushButton("🕘 History")
        self.history_btn.setObjectName("secondary")
        self.history_btn.clicked.connect(self.show_history)
        button_layout.addWidget(self.history_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        self.status_label = QLabel("Ready to convert your HTML...")
        self.status_label.setObjectName("status")
        main_layout.addWidget(self.status_label)
        self.text_editor.textChanged.connect(self.update_char_count)
        shortcuts_label = QLabel("Shortcuts: ⌘+Return = Open in Browser | ⌘+Q = Quit")
        shortcuts_label.setObjectName("shortcuts")
        shortcuts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(shortcuts_label)

    def center_on_screen(self):
        screen = QApplication.primaryScreen()
        geometry = screen.availableGeometry()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(geometry.center())
        self.move(frame_geometry.topLeft())

    def _init_history_storage(self) -> None:
        try:
            base_dir = os.path.join(
                os.path.expanduser("~"),
                "Library" if platform.system() == "Darwin" else "AppData/Local",
                "HTMLConverter",
            )
            os.makedirs(base_dir, exist_ok=True)
            self.history_file = os.path.join(base_dir, "history.json")
        except Exception:
            self.history_file = os.path.join(
                tempfile.gettempdir(), "html_converter_history.json"
            )
        self.load_history()

    def load_history(self) -> None:
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    cleaned = [
                        item
                        for item in data[: self.MAX_HISTORY]
                        if isinstance(item, dict)
                        and "title" in item
                        and "content" in item
                    ]
                    self.history_entries = cleaned
        except Exception:
            self.history_entries = []

    def save_history(self) -> None:
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(
                    self.history_entries[: self.MAX_HISTORY],
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception:
            pass

    def setup_shortcuts(self):
        safari_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        safari_shortcut.activated.connect(self.open_in_browser)
        safari_shortcut_mac = QShortcut(QKeySequence("Meta+Return"), self)
        safari_shortcut_mac.activated.connect(self.open_in_browser)

    def get_styled_wrapper(self, content):
        if not self.add_wrapper_checkbox.isChecked():
            return content
        if "<html" in content.lower() and "<body" in content.lower():
            return content
        wrapper = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Converted Document - {datetime.now().strftime("%B %d, %Y %I:%M %p")}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, {self.colors['dark_grey']} 0%, {self.colors['darker_grey']} 100%); color: {self.colors['white']}; min-height: 100vh; line-height: 1.8; padding: 60px 40px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: rgba(57, 57, 57, 0.4); backdrop-filter: blur(20px); border-radius: 20px; padding: 40px; border: 1px solid rgba(255, 90, 9, 0.2); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4); }}
        h1, h2, h3, h4, h5, h6 {{ color: {self.colors['light_orange']}; margin-bottom: 20px; margin-top: 30px; }}
        h1:first-child {{ margin-top: 0; }}
        a {{ color: {self.colors['deep_orange']}; text-decoration: none; transition: color 0.3s ease; }}
        a:hover {{ color: {self.colors['light_orange']}; text-decoration: underline; }}
        code {{ background: rgba(255, 90, 9, 0.1); color: {self.colors['light_orange']}; padding: 2px 6px; border-radius: 4px; font-family: 'SF Mono', monospace; font-variant-ligatures: none; -webkit-user-select: text; user-select: text; }}
        pre {{ background: {self.colors['darker_grey']}; padding: 20px; border-radius: 10px; overflow-x: auto; margin: 20px 0; border: 1px solid rgba(255, 90, 9, 0.2); -webkit-user-select: text; user-select: text; white-space: pre; tab-size: 4; -moz-tab-size: 4; }}
        blockquote {{ border-left: 4px solid {self.colors['deep_orange']}; padding-left: 20px; margin: 20px 0; font-style: italic; color: rgba(255, 255, 255, 0.8); }}
        hr {{ border: none; height: 1px; background: linear-gradient(90deg, transparent, {self.colors['orange_yellow']}, transparent); margin: 30px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255, 90, 9, 0.2); }}
        th {{ background: rgba(255, 90, 9, 0.1); color: {self.colors['light_orange']}; font-weight: 600; }}
        @media print {{ body {{ background: white; color: black; padding: 20px; }} .container {{ background: white; box-shadow: none; border: none; padding: 0; }} h1, h2, h3, h4, h5, h6 {{ color: {self.colors['dark_grey']}; }} a {{ color: {self.colors['orange_yellow']}; }} code {{ background: #f0f0f0; }} pre {{ background: #f5f5f5; border: 1px solid #ddd; }} }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>"""
        return wrapper

    def build_copyable_code_view(self, raw_html: str) -> str:
        """Return an escaped <pre><code> block for copyable HTML source.
        Avoid importing stdlib html due to module name conflict with this file.
        """

        def _escape(s: str) -> str:
            # Order matters: ampersand first
            s = s.replace("&", "&amp;")
            s = s.replace("<", "&lt;").replace(">", "&gt;")
            s = s.replace('"', "&quot;")
            return s

        escaped = _escape(raw_html)
        return (
            '<section class="code-view">\n'
            '  <h2 style="margin-bottom:12px;color:#ffa86b;font-weight:600;">HTML Source</h2>\n'
            "  <pre><code>" + escaped + "</code></pre>\n"
            "</section>"
        )

    def sanitize_for_pdf_copy(self, html: str) -> str:
        """Minimal sanitization so code copies cleanly from macOS Preview PDFs.
        - Normalize line endings
        - Remove zero-width, soft hyphen, BOM, and directional marks
        - Replace user-select:none with selectable text
        - Inject style to enforce selectable, monospace code and sane wrapping
        """
        # Normalize line endings
        s = html.replace("\r\n", "\n").replace("\r", "\n")
        # Replace NBSP and narrow NBSP with regular spaces
        s = s.replace("\xa0", " ").replace("\u202f", " ")
        # Remove BOM, zero-width, directional marks, and soft hyphens
        for ch in (
            "\ufeff",  # BOM
            "\u200b",
            "\u200c",
            "\u200d",  # zero width
            "\u2060",  # word joiner
            "\u200e",
            "\u200f",  # LRM/RLM
            "\u202a",
            "\u202b",
            "\u202c",
            "\u202d",
            "\u202e",  # bidi embedding/override
            "\u2066",
            "\u2067",
            "\u2068",
            "\u2069",  # bidi isolates
            "\u00ad",  # soft hyphen
        ):
            s = s.replace(ch, "")
        # Make non-selectable rules selectable
        for token in (
            "user-select: none",
            "user-select:none",
            "-webkit-user-select: none",
            "-webkit-user-select:none",
        ):
            s = s.replace(token, "user-select: text")
        for token in (
            "pointer-events: none",
            "pointer-events:none",
        ):
            s = s.replace(token, "pointer-events: auto")
        # Inject a small style block to enforce selection and monospace code
        lower = s.lower()
        style_block = """
<style id="pdf-copy-sanitize">
  body, pre, code, table, td, th, p, li, div { -webkit-user-select: text !important; user-select: text !important; }
  pre, code { font-family: SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace; font-variant-ligatures: none; tab-size: 4; -moz-tab-size: 4; }
  pre { white-space: pre; }
  @media print { pre { white-space: pre-wrap; word-break: normal; overflow-wrap: anywhere; } }
</style>
"""
        if "</head>" in lower and "pdf-copy-sanitize" not in lower:
            idx = lower.rfind("</head>")
            s = s[:idx] + style_block + s[idx:]
        elif "pdf-copy-sanitize" not in lower and (
            "<html" in lower or "<body" in lower
        ):
            s = style_block + s
        return s

    def inject_print_bands(
        self, html: str, band_text: str, top_mm: int = 12, bottom_mm: int = 12
    ) -> str:
        band_text = (band_text or "").strip()
        if not band_text:
            return html
        css = f"""
<style>
  .print-header, .print-footer {{ display: block !important; position: fixed; left: 0; right: 0; height: 8mm; padding: 2mm 6mm; background: transparent; z-index: 9999; font-size: 9pt; color: #2a6792; text-align: center; line-height: 1; white-space: nowrap; overflow: hidden; text-overflow: clip; }}
  .print-header {{ top: {top_mm}mm; }}
  .print-footer {{ bottom: {bottom_mm}mm; }}
  @media print {{ header, footer {{ display: none !important; }} body {{ padding-top: max(15mm, {top_mm + 3}mm); padding-bottom: max(15mm, {bottom_mm + 3}mm); }} }}
</style>
"""
        repeated = (band_text + " ") * 5
        bands = f"""
<div class="print-header" aria-hidden="true">{repeated}</div>
<div class="print-footer" aria-hidden="true">{repeated}</div>
"""
        lower = html.lower()
        if "</head>" in lower:
            idx = lower.rfind("</head>")
            html = html[:idx] + css + html[idx:]
        else:
            html = css + html
        lower = html.lower()
        if "<body" in lower:
            body_start = lower.find("<body")
            insert_after = lower.find(">", body_start) + 1
            html = html[:insert_after] + bands + html[insert_after:]
            return html
        if "</html>" in lower:
            idx = lower.rfind("</html>")
            html = html[:idx] + bands + html[idx:]
        else:
            html += bands
        return html

    def open_in_browser(self):
        html_content = self.text_editor.toPlainText()
        if not html_content.strip():
            QMessageBox.warning(
                self, "No Content", "Please paste some HTML code first!"
            )
            return
        try:
            processed_html = self.sanitize_for_pdf_copy(html_content)
            # When enabled, render the sanitized content as escaped code for PDF copyability
            if (
                getattr(self, "enable_pdf_copy_checkbox", None)
                and self.enable_pdf_copy_checkbox.isChecked()
            ):
                processed_html = self.build_copyable_code_view(processed_html)
            final_html = self.get_styled_wrapper(processed_html)
            if self.add_print_bands_checkbox.isChecked():
                final_html = self.inject_print_bands(
                    final_html,
                    self.print_band_text.text(),
                    self.top_offset_mm.value(),
                    self.bottom_offset_mm.value(),
                )
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            ) as f:
                f.write(final_html)
                temp_path = f.name
            webbrowser.open(f"file://{temp_path}", new=2)
            self._save_history_if_titled(html_content)
            self.status_label.setText(
                f"✅ Opened in browser | File: {temp_path} | Press ⌘+P to print"
            )
            self.save_history()
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Failed to open browser: {str(e)}")
            self.status_label.setText("❌ Browser open failed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")
            self.status_label.setText("❌ Error occurred")

    def save_title_to_history(self) -> None:
        html_content = self.text_editor.toPlainText()
        if not html_content.strip():
            self.status_label.setText("Nothing to save: editor is empty")
            return
        saved = self._save_history_if_titled(html_content)
        if saved:
            self.status_label.setText("✅ Saved to History")
            self._flash_history_preview()
        else:
            self.status_label.setText("ℹ️ Title missing or duplicate; not saved")

    def _save_history_if_titled(self, html_content: str) -> bool:
        title = (self.title_input.text() or "").strip()
        if not title:
            return False
        ts = datetime.now()
        timestamp_display = f"{ts.strftime('%I:%M:%S %p')} – {ts.strftime('%B %d, %Y')}"
        for e in self.history_entries:
            if e["title"] == title and e.get("content", "") == html_content:
                return False
        self.history_entries.insert(
            0,
            {
                "title": title,
                "timestamp": timestamp_display,
                "content": html_content,
            },
        )
        if len(self.history_entries) > self.MAX_HISTORY:
            self.history_entries = self.history_entries[: self.MAX_HISTORY]
        self.save_history()
        self.title_input.clear()
        return True

    def _flash_history_preview(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("History")
        dlg.resize(500, 120)
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("Saved to History"))
        QTimer.singleShot(600, dlg.accept)
        dlg.exec()

    def show_history(self):
        if getattr(self, "_history_dialog", None):
            self._populate_history_list()
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("History")
        dlg.resize(700, 500)
        self._history_dialog = dlg
        outer = QVBoxLayout(dlg)

        # Header with Clear button
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Saved Conversions"))
        header_layout.addStretch()
        clear_btn = QPushButton("Clear History")
        clear_btn.setFixedSize(120, 30)
        clear_btn.setStyleSheet(
            f"background-color: {self.colors['lighter_grey']}; font-size: 12px; padding: 5px;"
        )
        clear_btn.clicked.connect(self.clear_history)
        header_layout.addWidget(clear_btn)
        outer.addLayout(header_layout)

        scroll = QScrollArea(dlg)
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        container = QWidget()
        scroll.setWidget(container)
        v = QVBoxLayout(container)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(12)
        self._history_list_layout = v
        self._populate_history_list()
        dlg.exec()
        self._history_dialog = None
        self._history_list_layout = None

    def clear_history(self):
        if not self.history_entries:
            return
        reply = QMessageBox.question(
            self._history_dialog,
            "Confirm Clear",
            "Are you sure you want to clear all history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.history_entries = []
            self.save_history()
            self._populate_history_list()

    def _populate_history_list(self):
        layout = getattr(self, "_history_list_layout", None)
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        if not self.history_entries:
            layout.addWidget(
                QLabel("No saved items yet. Add a title and open in Safari to save.")
            )
            return
        for idx, entry in enumerate(self.history_entries):
            title = entry["title"]
            ts = entry.get("timestamp", "")
            btn = QPushButton(f"{idx+1}. {title} – {ts}")
            btn.setObjectName("historyItemButton")
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(partial(self._open_history_details, idx))
            layout.addWidget(btn)

    def update_char_count(self) -> None:
        text = self.text_editor.toPlainText()
        char_count = len(text)
        self.char_counter.setText(f"{char_count}")

    def _open_history_details(self, index: int) -> None:
        if index < 0 or index >= len(self.history_entries):
            return
        entry = self.history_entries[index]
        dlg = QDialog(self)
        dlg.setWindowTitle(entry["title"])
        dlg.resize(900, 600)
        layout = QVBoxLayout(dlg)
        header = QLabel(f"{entry['title']} — {entry.get('timestamp', '')}")
        layout.addWidget(header)
        code = QTextEdit()
        code.setReadOnly(True)
        code.setPlainText(entry.get("content", ""))
        layout.addWidget(code)
        actions = QHBoxLayout()
        reopen_btn = QPushButton("Open in Editor")
        copy_btn = QPushButton("Copy to Clipboard")
        delete_btn = QPushButton("Delete")
        actions.addWidget(reopen_btn)
        actions.addWidget(copy_btn)
        actions.addWidget(delete_btn)
        layout.addLayout(actions)

        def reopen():
            self.text_editor.setPlainText(entry.get("content", ""))
            self.title_input.setText(entry.get("title", ""))
            dlg.accept()

        def copy():
            QApplication.clipboard().setText(entry.get("content", ""))

        def delete():
            del self.history_entries[index]
            dlg.accept()
            self._populate_history_list()
            self.save_history()

        reopen_btn.clicked.connect(reopen)
        copy_btn.clicked.connect(copy)
        delete_btn.clicked.connect(delete)
        dlg.exec()
