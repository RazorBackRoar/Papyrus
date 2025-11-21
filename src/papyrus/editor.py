from PySide6.QtWidgets import QTextEdit, QApplication
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QColor, QPainter, QPen
from .utils import clean_pasted_html

class PagedTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._show_page_breaks = False
        self._line_color = QColor('#FF5A09')
        self.verticalScrollBar().valueChanged.connect(self._request_repaint)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.window().open_in_browser()
        else:
            super().keyPressEvent(event)

    def set_line_color(self, color_str: str) -> None:
        try:
            self._line_color = QColor(color_str)
        except Exception:
            self._line_color = QColor('#FF5A09')
        self._request_repaint()

    def _request_repaint(self):
        self.viewport().update()

    def set_show_page_breaks(self, show: bool) -> None:
        self._show_page_breaks = bool(show)
        self._request_repaint()

    def page_height_px(self) -> int:
        try:
            dpi = QApplication.primaryScreen().logicalDotsPerInch() or 96
        except Exception:
            dpi = 96
        return int(round(11.0 * dpi))

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._show_page_breaks:
            return
        painter = QPainter(self.viewport())
        pen = QPen(self._line_color)
        pen.setWidth(1)
        painter.setPen(pen)
        h = self.viewport().height()
        w = self.viewport().width()
        page_h = max(100, self.page_height_px())
        scroll_y = self.verticalScrollBar().value()
        first_y = page_h - (scroll_y % page_h)
        y = first_y
        while y < h:
            doc_y = y + scroll_y
            layout = self.document().documentLayout()
            blk = self.document().firstBlock()
            boundary = 0.0
            prev_bottom = 0.0
            while blk.isValid():
                rect = layout.blockBoundingRect(blk)
                top = rect.top()
                bottom = rect.bottom()
                if doc_y < top:
                    boundary = top
                    break
                if top <= doc_y <= bottom:
                    boundary = top if (doc_y - top) < (bottom - doc_y) else bottom
                    break
                prev_bottom = bottom
                blk = blk.next()
            else:
                boundary = prev_bottom
            y_view = boundary - scroll_y
            painter.drawLine(0, int(y_view), w, int(y_view))
            y += page_h
        painter.end()

    def insertFromMimeData(self, source):
        if source.hasText():
            text = source.text()
            cleaned = clean_pasted_html(text)
            if cleaned != text:
                new_source = QMimeData()
                new_source.setText(cleaned)
                super().insertFromMimeData(new_source)
                return
        super().insertFromMimeData(source)
