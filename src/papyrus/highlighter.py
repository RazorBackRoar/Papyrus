from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QTextDocument

class HTMLSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, doc: QTextDocument):
        super().__init__(doc)
        self.colors = {
            'tag': '#FF5A09',
            'attribute': '#EC7F37',
            'value': '#BE4F0C',
            'comment': '#666666',
            'keyword': '#EC7F37'
        }

    def highlightBlock(self, text):
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor(self.colors['tag']))
        start = text.find('<')
        while start >= 0:
            end = text.find('>', start)
            if end > start:
                self.setFormat(start, end - start + 1, tag_format)
            start = text.find('<', start + 1)
        if '<!--' in text:
            comment_format = QTextCharFormat()
            comment_format.setForeground(QColor(self.colors['comment']))
            start = text.find('<!--')
            end = text.find('-->')
            if end > start:
                self.setFormat(start, end - start + 3, comment_format)
