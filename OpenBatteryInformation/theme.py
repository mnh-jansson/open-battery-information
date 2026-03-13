"""
OBI-1 application stylesheet.
Industrial dark theme: charcoal background, cyan accent, crisp typography.
"""

STYLESHEET = """
/* ── Global ─────────────────────────────────────────────────────────────── */
* {
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 10pt;
    color: #E0E6ED;
}

QMainWindow, QWidget {
    background-color: #1C1F26;
}

/* ── Group boxes ─────────────────────────────────────────────────────────── */
QGroupBox {
    background-color: #22262F;
    border: 1px solid #2E3340;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 6px;
    font-weight: 600;
    font-size: 9pt;
    color: #7A8499;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    left: 10px;
    color: #7A8499;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
QPushButton {
    background-color: #2A2F3A;
    border: 1px solid #3A4050;
    border-radius: 5px;
    padding: 6px 14px;
    color: #C8D0DC;
    font-weight: 500;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #323848;
    border-color: #00B4CC;
    color: #FFFFFF;
}
QPushButton:pressed {
    background-color: #00B4CC;
    border-color: #00B4CC;
    color: #0D1117;
}
QPushButton:disabled {
    background-color: #1E2229;
    border-color: #282D38;
    color: #3E4555;
}

/* ── Primary / accent button (assign via setProperty) ─────────────────────── */
QPushButton[accent="true"] {
    background-color: #007A8C;
    border-color: #00B4CC;
    color: #FFFFFF;
    font-weight: 600;
}
QPushButton[accent="true"]:hover {
    background-color: #00B4CC;
}
QPushButton[accent="true"]:pressed {
    background-color: #005F6B;
}

/* ── Danger button ───────────────────────────────────────────────────────── */
QPushButton[danger="true"] {
    background-color: #4A1C1C;
    border-color: #8B2020;
    color: #FF7070;
}
QPushButton[danger="true"]:hover {
    background-color: #8B2020;
    color: #FFFFFF;
}

/* ── ComboBox ────────────────────────────────────────────────────────────── */
QComboBox {
    background-color: #2A2F3A;
    border: 1px solid #3A4050;
    border-radius: 5px;
    padding: 5px 10px;
    color: #C8D0DC;
    min-height: 28px;
    selection-background-color: #007A8C;
}
QComboBox:hover {
    border-color: #00B4CC;
}
QComboBox:focus {
    border-color: #00B4CC;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #7A8499;
    width: 0;
    height: 0;
    margin-right: 6px;
}
QComboBox QAbstractItemView {
    background-color: #22262F;
    border: 1px solid #3A4050;
    selection-background-color: #007A8C;
    selection-color: #FFFFFF;
    outline: none;
}

/* ── SpinBox ─────────────────────────────────────────────────────────────── */
QSpinBox {
    background-color: #2A2F3A;
    border: 1px solid #3A4050;
    border-radius: 5px;
    padding: 5px 8px;
    color: #C8D0DC;
    min-height: 28px;
}
QSpinBox:hover  { border-color: #00B4CC; }
QSpinBox:focus  { border-color: #00B4CC; }
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #32384A;
    border: none;
    width: 18px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #007A8C;
}

/* ── Labels ──────────────────────────────────────────────────────────────── */
QLabel {
    color: #9BA5B5;
    background: transparent;
}

/* ── TextEdit (debug log) ────────────────────────────────────────────────── */
QTextEdit {
    background-color: #13151A;
    border: 1px solid #2A2F3A;
    border-radius: 4px;
    color: #5A9E6F;          /* terminal-green text */
    font-family: "Consolas", "Cascadia Code", "Courier New", monospace;
    font-size: 9pt;
    selection-background-color: #007A8C;
}

/* ── TreeWidget ──────────────────────────────────────────────────────────── */
QTreeWidget {
    background-color: #1C1F26;
    alternate-background-color: #20242C;
    border: 1px solid #2E3340;
    border-radius: 5px;
    gridline-color: #2A2F3A;
    outline: none;
}
QTreeWidget::item {
    padding: 4px 6px;
    border: none;
}
QTreeWidget::item:selected {
    background-color: #007A8C;
    color: #FFFFFF;
}
QTreeWidget::item:hover:!selected {
    background-color: #262B36;
}
QHeaderView::section {
    background-color: #22262F;
    border: none;
    border-right: 1px solid #2E3340;
    border-bottom: 1px solid #2E3340;
    padding: 5px 8px;
    color: #7A8499;
    font-weight: 600;
    font-size: 9pt;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #1C1F26;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #3A4050;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #00B4CC; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: #1C1F26;
    height: 8px;
}
QScrollBar::handle:horizontal {
    background: #3A4050;
    border-radius: 4px;
    min-width: 24px;
}
QScrollBar::handle:horizontal:hover { background: #00B4CC; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Splitter ────────────────────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #2E3340;
    width: 1px;
}

/* ── MessageBox ──────────────────────────────────────────────────────────── */
QMessageBox {
    background-color: #22262F;
}
QMessageBox QLabel {
    color: #C8D0DC;
}
"""
