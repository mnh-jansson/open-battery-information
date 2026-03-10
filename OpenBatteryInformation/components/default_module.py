from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt


class DefaultModule(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        icon_lbl = QLabel("⚡")
        icon_lbl.setStyleSheet("font-size: 48pt; color: #00B4CC;")
        icon_lbl.setAlignment(Qt.AlignCenter)

        title = QLabel("OBI-1")
        title.setStyleSheet(
            "font-size: 28pt; font-weight: 700; color: #00B4CC; letter-spacing: 4px;"
        )
        title.setAlignment(Qt.AlignCenter)

        tagline = QLabel("Open Battery Instrument")
        tagline.setStyleSheet(
            "font-size: 11pt; color: #3E4555; letter-spacing: 2px;")
        tagline.setAlignment(Qt.AlignCenter)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFixedWidth(200)
        divider.setStyleSheet("color: #2E3340;")

        hint = QLabel(
            "Select a module and interface\nfrom the sidebar to begin.")
        hint.setStyleSheet(
            "font-size: 10pt; color: #5A6070; line-height: 1.6;")
        hint.setAlignment(Qt.AlignCenter)

        for widget in (icon_lbl, title, tagline, divider, hint):
            layout.addWidget(widget, alignment=Qt.AlignCenter)
