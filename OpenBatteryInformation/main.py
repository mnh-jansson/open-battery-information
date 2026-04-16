import os
import sys
import importlib

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QSplitter, QGroupBox, QComboBox, QTextEdit, QFrame,
    QStatusBar, QLabel
)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, QDateTime

from components.default_module import DefaultModule
from theme import STYLESHEET

APP_NAME = "OBI-1"
APP_VERSION = "1.0.0"


class OBI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME}  ·  v{APP_VERSION}")
        self.resize(1270, 720)
        self.setMinimumSize(900, 540)
        self._set_icon("icon.png")

        self.main_app = None
        self.current_interface = None
        self._module_cache:    dict = {}
        self._interface_cache: dict = {}
        self._module_names:    dict = {}   # display_name -> internal_name
        self._interface_names: dict = {}

        self._build_ui()
        self._build_status_bar()

        self._load_plugins("modules",    self._module_names,
                           self.module_combo,    "— select module —")
        self._load_plugins("interfaces", self._interface_names,
                           self.interface_combo, "— select interface —")
        self._show_default()

        # Pre-select defaults if available
        #self._preselect(self.module_combo,    self._module_names,
                        #"Makita LXT",   self._on_module_selected)
        #self._preselect(self.interface_combo, self._interface_names,
                        #"Arduino OBI",  self._on_interface_selected)

    # ──────────────────────────────────────────── UI construction

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Horizontal splitter: sidebar | main content
        h_splitter = QSplitter(Qt.Horizontal)
        h_splitter.setChildrenCollapsible(False)

        h_splitter.addWidget(self._build_sidebar())

        self.main_window = QWidget()
        self.main_layout = QVBoxLayout(self.main_window)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        h_splitter.addWidget(self.main_window)
        h_splitter.setSizes([220, 1050])

        # Vertical splitter: top (sidebar+main) | debug log
        v_splitter = QSplitter(Qt.Vertical)
        v_splitter.setChildrenCollapsible(False)
        v_splitter.addWidget(h_splitter)
        v_splitter.addWidget(self._build_debug_frame())
        v_splitter.setSizes([580, 130])
        v_splitter.setHandleWidth(4)

        root.addWidget(v_splitter)

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(
            "#sidebar { background-color: #181B22; border-right: 1px solid #2E3340; }")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 14, 10, 14)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignTop)

        # App title in sidebar
        title_lbl = QLabel(APP_NAME)
        title_lbl.setStyleSheet(
            "font-size: 15pt; font-weight: 700; color: #00B4CC; letter-spacing: 2px;"
        )
        title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)

        ver_lbl = QLabel(f"v{APP_VERSION}")
        ver_lbl.setStyleSheet(
            "font-size: 8pt; color: #3E4555; letter-spacing: 1px;")
        ver_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(ver_lbl)

        layout.addSpacing(8)

        # Module selection
        mod_group = QGroupBox("Module")
        mod_layout = QVBoxLayout(mod_group)
        mod_layout.setContentsMargins(8, 14, 8, 8)
        self.module_combo = QComboBox()
        # activated fires only on user interaction, not programmatic changes
        self.module_combo.activated.connect(self._on_module_selected)
        mod_layout.addWidget(self.module_combo)
        layout.addWidget(mod_group)

        # Interface selection
        iface_group = QGroupBox("Interface")
        iface_layout = QVBoxLayout(iface_group)
        iface_layout.setContentsMargins(8, 14, 8, 8)
        self.interface_combo = QComboBox()
        self.interface_combo.activated.connect(self._on_interface_selected)
        iface_layout.addWidget(self.interface_combo)

        self.interface_wireframe = QFrame()
        self.interface_wireframe_layout = QVBoxLayout(self.interface_wireframe)
        self.interface_wireframe_layout.setContentsMargins(0, 6, 0, 0)
        self.interface_wireframe_layout.setSpacing(4)
        iface_layout.addWidget(self.interface_wireframe)

        layout.addWidget(iface_group)
        layout.addStretch()
        return sidebar

    def _build_debug_frame(self):
        group = QGroupBox("Debug Log")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(8, 14, 8, 8)
        self.debug_text = QTextEdit()
        self.debug_text.setReadOnly(True)
        layout.addWidget(self.debug_text)
        return group

    def _build_status_bar(self):
        bar = QStatusBar()
        bar.setStyleSheet(
            "QStatusBar { background: #181B22; border-top: 1px solid #2E3340; "
            "color: #3E4555; font-size: 8pt; padding: 2px 8px; }"
        )
        self._status_lbl = QLabel("Ready")
        bar.addPermanentWidget(self._status_lbl)
        self.setStatusBar(bar)

    # ──────────────────────────────────────────── icon / resources

    def _set_icon(self, icon_path):
        full_path = self._resource(icon_path)
        if os.path.exists(full_path):
            self.setWindowIcon(QIcon(full_path))

    def _resource(self, relative_path: str) -> str:
        base = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base, relative_path)

    # ──────────────────────────────────────────── plugin loader (generic)

    def _load_plugins(self, subdir: str, names_dict: dict,
                      combo: QComboBox, placeholder: str):
        """Discover plugins in *subdir*, fill *names_dict* and *combo*.
        Works both in normal Python and in a PyInstaller frozen bundle.
        """
        directory = self._resource(subdir)

        if not os.path.isdir(directory):
            self.update_debug(
                f"[WARN] Plugin directory not found: {directory}")
            combo.addItems([placeholder])
            return

        # Collect module names from .py files (dev) or compiled .pyc files (frozen)
        names = set()
        for entry in os.listdir(directory):
            if entry.startswith("_"):
                continue
            if entry.endswith(".py"):
                names.add(entry[:-3])
            elif entry.endswith(".pyc"):
                names.add(entry[:-4])

        for name in sorted(names):
            try:
                mod = importlib.import_module(f"{subdir}.{name}")
                display = mod.get_display_name()
                names_dict[display] = name
            except Exception as e:
                self.update_debug(
                    f"[WARN] Failed to load {subdir}/{name}: {e}")

        combo.addItems([placeholder] + list(names_dict))

    def _preselect(self, combo: QComboBox, names_dict: dict, display_name: str, slot):
        """Select *display_name* in *combo* and trigger *slot* if it exists."""
        if display_name in names_dict:
            combo.setCurrentText(display_name)
            slot(combo.currentIndex())

    # ──────────────────────────────────────────── display helpers

    def _show_default(self):
        self._clear_main()
        self.main_layout.addWidget(DefaultModule())

    def _clear_main(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

    def _clear_interface_wireframe(self):
        while self.interface_wireframe_layout.count():
            item = self.interface_wireframe_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

    # ──────────────────────────────────────────── slots

    def _on_module_selected(self, index: int):
        display = self.module_combo.currentText()
        internal = self._module_names.get(display)
        if not internal:
            return

        mod = self._get_cached(internal, "modules", self._module_cache)
        if mod is None:
            return

        self._clear_main()
        try:
            self.main_app = mod.ModuleApplication(self.main_window, None, self)
        except Exception as e:
            self.update_debug(
                f"[ERROR] Init failed for module '{internal}': {e}")
            self.main_app = None
            return

        self.main_app.set_interface(self.current_interface)
        self.main_layout.addWidget(self.main_app)
        self._set_status(f"Module loaded: {display}")

    def _on_interface_selected(self, index: int):
        display = self.interface_combo.currentText()
        internal = self._interface_names.get(display)
        if not internal:
            return

        iface_mod = self._get_cached(
            internal, "interfaces", self._interface_cache)
        if iface_mod is None:
            return

        self._clear_interface_wireframe()
        self.current_interface = iface_mod.Interface(
            self.interface_wireframe, self)
        self.interface_wireframe_layout.addWidget(self.current_interface)

        if self.current_interface and hasattr(self.current_interface, 'connected'):
            self.current_interface.connected.connect(
                self._on_interface_connected)
        if self.current_interface and hasattr(self.current_interface, 'disconnected'):
            self.current_interface.disconnected.connect(
                self._on_interface_disconnected_dropdowns)

        if self.main_app is not None:
            self.main_app.set_interface(self.current_interface)

        self._set_status(f"Interface: {display}")

    def _on_interface_connected(self):
        self.module_combo.setEnabled(False)
        self.interface_combo.setEnabled(False)

    def _on_interface_disconnected_dropdowns(self):
        self.module_combo.setEnabled(True)
        self.interface_combo.setEnabled(True)

    # ──────────────────────────────────────────── generic cache

    def _get_cached(self, name: str, subdir: str, cache: dict):
        """Return cached import, importing on first call. Returns None on failure."""
        if name not in cache:
            try:
                cache[name] = importlib.import_module(f"{subdir}.{name}")
                self.update_debug(f"[INFO] Imported {subdir}/{name}")
            except Exception as e:
                self.update_debug(
                    f"[ERROR] Import failed for {subdir}/{name}: {e}")
                return None
        else:
            self.update_debug(f"[INFO] Using cached {subdir}/{name}")
        return cache[name]

    # ──────────────────────────────────────────── close event

    def closeEvent(self, event):
        """Ensure the serial port is closed cleanly when the window is closed."""
        if (self.current_interface is not None
                and hasattr(self.current_interface, 'serial')
                and self.current_interface.serial.is_open):
            self.current_interface.serial.close()
        event.accept()

    # ──────────────────────────────────────────── debug / status

    def update_debug(self, message: str):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
        self.debug_text.append(
            f"<span style='color:#3E6E8C'>[{timestamp}]</span> {message}")
        self.debug_text.ensureCursorVisible()

    def _set_status(self, message: str):
        self._status_lbl.setText(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = OBI()
    window.show()
    sys.exit(app.exec())
