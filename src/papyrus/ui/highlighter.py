"""HTML syntax highlighter for the text editor."""
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QTextDocument
from PySide6.QtCore import QRegularExpression

class HTMLSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for HTML code with custom color scheme."""

    def __init__(self, doc: QTextDocument):
        """Initialize the syntax highlighter.

        Args:
            doc: QTextDocument to apply highlighting to
        """
        super().__init__(doc)
        self.colors = {
            'tag': '#FF5A09',       # Deep Orange
            'attribute': '#EC7F37', # Light Orange
            'value': '#BE4F0C',     # Orange Yellow (Darker)
            'comment': '#666666',   # Grey
            'doctype': '#2a9df4',   # Bright Blue
            'entity': '#d19a66'     # Soft Orange/Brown
        }
        
        self.highlighting_rules = []

        # Tag format (e.g., <div, </div>, <br/>)
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor(self.colors['tag']))
        tag_format.setFontWeight(700)  # Bold tags
        self.highlighting_rules.append((QRegularExpression(r"</?[\w-]+(?:\s|/?>)"), tag_format))
        self.highlighting_rules.append((QRegularExpression(r">"), tag_format))

        # Attribute format (e.g., class=, id=)
        attr_format = QTextCharFormat()
        attr_format.setForeground(QColor(self.colors['attribute']))
        self.highlighting_rules.append((QRegularExpression(r"\s[\w-]+="), attr_format))

        # Value format (e.g., "container", 'header')
        value_format = QTextCharFormat()
        value_format.setForeground(QColor(self.colors['value']))
        self.highlighting_rules.append((QRegularExpression(r"\"[^\"]*\""), value_format))
        self.highlighting_rules.append((QRegularExpression(r"'[^']*'"), value_format))

        # Doctype format
        doctype_format = QTextCharFormat()
        doctype_format.setForeground(QColor(self.colors['doctype']))
        doctype_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression(r"<!DOCTYPE[^>]*>"), doctype_format))

        # Entity format (e.g., &nbsp;)
        entity_format = QTextCharFormat()
        entity_format.setForeground(QColor(self.colors['entity']))
        self.highlighting_rules.append((QRegularExpression(r"&[a-zA-Z0-9#]+;"), entity_format))

        # Comment format
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(self.colors['comment']))
        self.comment_format.setFontItalic(True)
        
        self.comment_start = QRegularExpression(r"<!--")
        self.comment_end = QRegularExpression(r"-->")

    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text.

        Args:
            text: Text block to highlight
        """
        # Apply regular expression rules
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        # Handle multi-line comments
        self.setCurrentBlockState(0)
        
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start.match(text).capturedStart()

        while start_index >= 0:
            match = self.comment_end.match(text, start_index)
            end_index = match.capturedStart()
            comment_length = 0
            
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + match.capturedLength()
            
            self.setFormat(start_index, comment_length, self.comment_format)
            start_index = self.comment_start.match(text, start_index + comment_length).capturedStart()
