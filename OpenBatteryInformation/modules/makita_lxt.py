from PySide6.QtWidgets import (
    QApplication,
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QPushButton, QTreeWidget, QTreeWidgetItem,
    QLabel, QMessageBox, QHeaderView, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush, QFont

# ──────────────────────────────────────────────────────────────────────────────
# Command definitions
# ──────────────────────────────────────────────────────────────────────────────
MODEL_CMD = [0x01, 0x02, 0x10, 0xCC, 0xDC, 0x0C]
READ_DATA_REQUEST = [0x01, 0x04, 0x1D, 0xCC, 0xD7, 0x00, 0x00, 0xFF]
TESTMODE_CMD = [0x01, 0x03, 0x09, 0x33, 0xD9, 0x96, 0xA5]
LEDS_ON_CMD = [0x01, 0x02, 0x09, 0x33, 0xDA, 0x31]
LEDS_OFF_CMD = [0x01, 0x02, 0x09, 0x33, 0xDA, 0x34]
RESET_ERROR_CMD = [0x01, 0x02, 0x09, 0x33, 0xDA, 0x04]
CHARGER_CMD = [0x01, 0x02, 0x20, 0xCC, 0xF0, 0x00]
READ_MSG_CMD = [0x01, 0x02, 0x28, 0x33, 0xAA, 0x00]
CLEAR_CMD = [0x01, 0x02, 0x00, 0xCC, 0xF0, 0x00]
STORE_CMD = [0x01, 0x02, 0x00, 0x33, 0x55, 0xA5]
CLEAN_FRAME_CMD = [
    0x01, 0x22, 0x00, 0x33, 0x33, 0x0F, 0x00, 0xF1, 0x26, 0xBD,
    0x13, 0x14, 0x58, 0x00, 0x00, 0x94, 0x94, 0x40, 0x21, 0xD0,
    0x80, 0x02, 0x4E, 0x23, 0xD0, 0x8E, 0x45, 0x60, 0x1A, 0x00,
    0x03, 0x02, 0x02, 0x0E, 0x20, 0x00, 0x30, 0x01, 0x83,
]

# F0513-specific commands
F0513_VCELL_CMDS = [
    [0x01, 0x01, 0x02, 0xCC, 0x31],   # cell 1
    [0x01, 0x01, 0x02, 0xCC, 0x32],   # cell 2
    [0x01, 0x01, 0x02, 0xCC, 0x33],   # cell 3
    [0x01, 0x01, 0x02, 0xCC, 0x34],   # cell 4
    [0x01, 0x01, 0x02, 0xCC, 0x35],   # cell 5
]
F0513_TEMP_CMD = [0x01, 0x01, 0x02, 0xCC, 0x52]
F0513_MODEL_CMD = [0x01, 0x00, 0x02, 0x31]
F0513_TESTMODE_CMD = [0x01, 0x01, 0x00, 0xCC, 0x99]

# ──────────────────────────────────────────────────────────────────────────────
# Table layout — order defines display order; empty string = cleared state
# ──────────────────────────────────────────────────────────────────────────────
INITIAL_DATA: dict[str, str] = {
    "Model":                    "",
    "Charge count*":            "",
    "State":                    "",
    "Status code":              "",
    "Pack Voltage":             "",
    "Cell 1 Voltage":           "",
    "Cell 2 Voltage":           "",
    "Cell 3 Voltage":           "",
    "Cell 4 Voltage":           "",
    "Cell 5 Voltage":           "",
    "Cell Voltage Difference":  "",
    "Temperature Sensor 1":     "",
    "Temperature Sensor 2":     "",
    "ROM ID":                   "",
    "Manufacturing date":       "",
    "Battery message":          "",
    "Capacity":                 "",
    "Battery type":             "",
}

ROW_EVEN = QColor("#1C1F26")
ROW_ODD = QColor("#20242C")


def get_display_name() -> str:
    return "Makita LXT"


class ModuleApplication(QWidget):
    def __init__(self, parent=None, interface_module=None, obi_instance=None):
        super().__init__(parent)
        self.interface = None
        self.obi_instance = obi_instance
        # "" = standard protocol,  "F0513" = F0513 variant,  None = unknown / cleared
        self.command_version: str | None = None

        self._build_ui()
        self._insert_battery_data(INITIAL_DATA)

    # ── public API ────────────────────────────────────────────────────────────

    def set_interface(self, interface_instance):
        self.interface = interface_instance

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        # Title
        title = QLabel(get_display_name())
        title.setStyleSheet(
            "font-size: 18pt; font-weight: 700; color: #00B4CC; letter-spacing: 1px;"
        )
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        subtitle = QLabel("Li-ion Battery Diagnostics")
        subtitle.setStyleSheet(
            "font-size: 9pt; color: #3E4555; letter-spacing: 1px;")
        subtitle.setAlignment(Qt.AlignCenter)
        root.addWidget(subtitle)

        # Thin divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #2E3340; margin: 2px 0;")
        root.addWidget(divider)

        root.addWidget(self._build_button_row())
        root.addWidget(self._build_tree(), stretch=1)
        root.addLayout(self._build_bottom_bar())

    def _build_button_row(self) -> QWidget:
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(10)
        grid.setContentsMargins(0, 0, 0, 0)

        # Read data
        read_group = QGroupBox("Read Data")
        read_layout = QVBoxLayout(read_group)
        read_layout.setContentsMargins(10, 18, 10, 10)
        self.btn_read_model = QPushButton("Read Battery Model")
        self.btn_read_data = QPushButton("Read Battery Data")
        self.btn_read_data.setEnabled(False)
        # btn_read_model is intentionally NOT in _action_buttons:
        #   it starts enabled and should always remain enabled so the user
        #   can re-read after clearing. _enable_all_buttons enables the
        #   data/LED/reset buttons; _disable_action_buttons disables them.
        for btn in (self.btn_read_model, self.btn_read_data):
            read_layout.addWidget(btn)
        self.btn_read_model.clicked.connect(self._on_read_static_click)
        self.btn_read_data.clicked.connect(self._on_read_data_click)

        # Function test
        fn_group = QGroupBox("Function Test")
        fn_layout = QVBoxLayout(fn_group)
        fn_layout.setContentsMargins(10, 18, 10, 10)
        self.btn_leds_on = QPushButton("LED Test  ON")
        self.btn_leds_off = QPushButton("LED Test  OFF")
        for btn in (self.btn_leds_on, self.btn_leds_off):
            btn.setEnabled(False)
            fn_layout.addWidget(btn)
        self.btn_leds_on.clicked.connect(self._on_all_leds_on_click)
        self.btn_leds_off.clicked.connect(self._on_all_leds_off_click)

        # Reset
        reset_group = QGroupBox("Reset Battery")
        reset_layout = QVBoxLayout(reset_group)
        reset_layout.setContentsMargins(10, 18, 10, 10)
        self.btn_clear_errors = QPushButton("Clear Errors")
        self.btn_reset_message = QPushButton("Reset Battery Message")
        for btn in (self.btn_clear_errors, self.btn_reset_message):
            btn.setEnabled(False)
            reset_layout.addWidget(btn)
        self.btn_clear_errors.clicked.connect(self._on_reset_errors_click)
        self.btn_reset_message.clicked.connect(self._on_reset_message_click)

        grid.addWidget(read_group,  0, 0)
        grid.addWidget(fn_group,    0, 1)
        grid.addWidget(reset_group, 0, 2)

        self._action_buttons: list[QPushButton] = [
            self.btn_read_data,
            self.btn_leds_on, self.btn_leds_off,
            self.btn_clear_errors, self.btn_reset_message,
        ]
        return container

    def _build_tree(self) -> QTreeWidget:
        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Parameter", "Value"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tree.setAlternatingRowColors(
            False)   # colours set manually per-row
        self.tree.setRootIsDecorated(False)
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        return self.tree

    def _build_bottom_bar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 4, 0, 0)

        note = QLabel(
            "* Charge count is approximate  ·  Select rows then Copy to export")
        note.setStyleSheet("font-size: 8pt; color: #3E4555;")
        layout.addWidget(note, stretch=1)

        copy_btn = QPushButton("Copy Selected")
        copy_btn.setFixedWidth(110)
        copy_btn.clicked.connect(self._copy_to_clipboard)

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedWidth(80)
        clear_btn.clicked.connect(self._clear_data)

        layout.addWidget(copy_btn)
        layout.addWidget(clear_btn)
        return layout

    # ── helpers ───────────────────────────────────────────────────────────────

    def _enable_all_buttons(self):
        for btn in self._action_buttons:
            btn.setEnabled(True)

    def _disable_action_buttons(self):
        for btn in self._action_buttons:
            btn.setEnabled(False)

    def _require_interface(self) -> bool:
        if not self.interface:
            QMessageBox.critical(self, "No Interface",
                                 "Please select an interface first.")
            return False
        return True

    def _log(self, msg: str):
        if self.obi_instance:
            self.obi_instance.update_debug(msg)

    @staticmethod
    def _nibble_swap(byte: int) -> int:
        return ((byte & 0xF0) >> 4) | ((byte & 0x0F) << 4)

    @staticmethod
    def _fmt_voltage(v: float) -> str:
        return f"{v:.3f} V"

    @staticmethod
    def _fmt_temp(t) -> str:
        return f"{t:.2f} °C" if t != "" else ""

    # ── model detection ───────────────────────────────────────────────────────

    def _try_get_model(self) -> str | None:
        """
        Attempt standard model read.
        Returns the model string on success, None if the battery doesn't respond
        to this protocol (so the caller can try the next probe).
        Raises only on hard errors (port closed, etc.).
        """
        try:
            response = self.interface.request(MODEL_CMD)
            self.command_version = ""
            self._enable_all_buttons()
            return response[2:9].decode('utf-8').strip()
        except Exception as e:
            self._log(f"[INFO] Standard model probe failed: {e}")
            return None

    def _try_get_f0513_model(self) -> str | None:
        """
        Attempt F0513 model read.
        Returns the model string on success, None if the battery doesn't respond.
        Raises only on hard errors.
        """
        try:
            response = self.interface.request(F0513_MODEL_CMD)
            self.interface.request(CLEAR_CMD)
            self.command_version = "F0513"
            self.btn_read_data.setEnabled(True)
            QMessageBox.warning(self, "Limited Support",
                                "F0513 battery detected.\n"
                                "Only voltage/temperature diagnostics are supported.")
            return f"BL{response[2]:X}{response[3]:X}"
        except Exception as e:
            self._log(f"[INFO] F0513 model probe failed: {e}")
            return None

    # ── command handlers ──────────────────────────────────────────────────────

    def _on_read_static_click(self):
        if not self._require_interface():
            return

        try:
            response = self.interface.request(READ_MSG_CMD)
        except Exception as e:
            QMessageBox.critical(self, "Read Error", str(e))
            return

        swapped = bytearray([self._nibble_swap(response[37]),
                             self._nibble_swap(response[36])])[::-1]
        charge_count = int.from_bytes(swapped, 'big') & 0x0FFF
        lock_status = "LOCKED" if (response[30] & 0x0F) > 0 else "UNLOCKED"

        self._insert_battery_data({
            "ROM ID":             ' '.join(f'{b:02X}' for b in response[2:10]),
            "Battery message":    ' '.join(f'{b:02X}' for b in response[10:42]),
            "Charge count*":      charge_count,
            "State":              lock_status,
            "Status code":        f'{response[29]:02X}',
            "Manufacturing date": f'{response[4]:02}/{response[3]:02}/20{response[2]:02}',
            "Capacity":           f'{self._nibble_swap(response[26]) / 10} Ah',
            "Battery type":       self._nibble_swap(response[21]),
        })

        # Try each model probe in order; use the first one that succeeds.
        for probe in (self._try_get_model, self._try_get_f0513_model):
            model = probe()
            if model is not None:
                self._insert_battery_data({"Model": model})
                return

        QMessageBox.critical(self, "Unsupported Battery",
                             "Battery is present but no supported protocol was detected.")

    def _on_read_data_click(self):
        if not self._require_interface():
            return
        try:
            if self.command_version == 'F0513':
                # F0513 requires two CLEAR commands before individual cell reads.
                self.interface.request(CLEAR_CMD)
                self.interface.request(CLEAR_CMD)
                cell_resp = [self.interface.request(
                    cmd) for cmd in F0513_VCELL_CMDS]
                voltages = [int.from_bytes(
                    r[2:4], 'little') / 1000 for r in cell_resp]
                temp_r = self.interface.request(F0513_TEMP_CMD)
                t_cell = int.from_bytes(temp_r[2:4], 'little') / 100
                t_mosfet = ""
                # F0513 has no hardware pack voltage register — derive from cell sum.
                v_pack = round(sum(voltages), 3)
            else:
                r = self.interface.request(READ_DATA_REQUEST)
                # r[2:4]  = hardware-reported pack voltage (BMS measurement)
                # r[4:14] = five cell voltages, 2 bytes each, little-endian mV
                # Pack voltage is kept as the hardware value rather than summing cells,
                # because the BMS timing may differ slightly from the arithmetic sum.
                v_pack = int.from_bytes(r[2:4], 'little') / 1000
                voltages = [int.from_bytes(r[i:i+2], 'little') / 1000
                            for i in range(4, 14, 2)]
                t_cell = int.from_bytes(r[16:18], 'little') / 100
                t_mosfet = int.from_bytes(r[18:20], 'little') / 100

            v_diff = round(max(voltages) - min(voltages), 3)

            self._insert_battery_data({
                "Pack Voltage":            self._fmt_voltage(v_pack),
                "Cell 1 Voltage":          self._fmt_voltage(voltages[0]),
                "Cell 2 Voltage":          self._fmt_voltage(voltages[1]),
                "Cell 3 Voltage":          self._fmt_voltage(voltages[2]),
                "Cell 4 Voltage":          self._fmt_voltage(voltages[3]),
                "Cell 5 Voltage":          self._fmt_voltage(voltages[4]),
                "Cell Voltage Difference": self._fmt_voltage(v_diff),
                "Temperature Sensor 1":    self._fmt_temp(t_cell),
                "Temperature Sensor 2":    self._fmt_temp(t_mosfet),
            })

        except Exception as e:
            QMessageBox.critical(self, "Read Error",
                                 f"Failed to read battery data:\n{e}")

    def _on_all_leds_on_click(self):
        if not self._require_interface():
            return
        try:
            self.interface.request(TESTMODE_CMD)
            self.interface.request(LEDS_ON_CMD)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to turn LEDs on:\n{e}")

    def _on_all_leds_off_click(self):
        if not self._require_interface():
            return
        try:
            cmd = F0513_TESTMODE_CMD if self.command_version == 'F0513' else TESTMODE_CMD
            self.interface.request(cmd)
            self.interface.request(LEDS_OFF_CMD)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to turn LEDs off:\n{e}")

    def _on_reset_errors_click(self):
        if not self._require_interface():
            return
        try:
            self.interface.request(TESTMODE_CMD)
            self.interface.request(RESET_ERROR_CMD)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to reset errors:\n{e}")

    def _on_reset_message_click(self):
        if not self._require_interface():
            return
        # TODO: Read current frame from battery, zero nibble 0, write back via
        #       CHARGER_CMD + modified frame + STORE_CMD.
        #       Do NOT use the hardcoded CLEAN_FRAME_CMD until implemented — it
        #       would overwrite battery-specific calibration data.
        QMessageBox.information(self, "Not Available",
                                "Reset battery message is under development.\n"
                                "Check back in a future version.")

    # ── tree helpers ──────────────────────────────────────────────────────────

    def _insert_battery_data(self, data: dict):
        for parameter, value in data.items():
            items = self.tree.findItems(parameter, Qt.MatchExactly, 0)
            if items:
                items[0].setText(1, str(value))
            else:
                row = self.tree.topLevelItemCount()
                item = QTreeWidgetItem([parameter, str(value)])
                colour = ROW_EVEN if row % 2 == 0 else ROW_ODD
                for col in range(2):
                    item.setBackground(col, QBrush(colour))
                # Make the parameter name slightly dimmer
                item.setForeground(0, QBrush(QColor("#7A8499")))
                self.tree.addTopLevelItem(item)

    def _copy_to_clipboard(self):
        selected = self.tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Nothing Selected",
                                "Select one or more rows to copy.")
            return
        # Tab-separated Parameter<TAB>Value — pastes cleanly into Excel / LibreOffice Calc
        lines = [f"{item.text(0)}\t{item.text(1)}" for item in selected]
        QApplication.clipboard().setText('\n'.join(lines))
        QMessageBox.information(self, "Copied",
                                f"{len(lines)} row(s) copied to clipboard.")

    def _clear_data(self):
        """Reset table to empty state and restore UI to pre-read condition."""
        self._insert_battery_data(INITIAL_DATA)
        self.command_version = None
        self._disable_action_buttons()
