"""
makita_lxt.py  —  Makita LXT 18V battery diagnostics module for OBI-1.

Supports battery types: 0 (standard/newest), 2, 3, 5 (F0513), 6 (10-cell BL36xx).

Command frame format used by ArduinoOBI interface:
  Byte 0: 0x01  (framing start)
  Byte 1: <number of 1-wire bytes to write>
  Byte 2: <number of response bytes expected>
  Byte 3+: 1-wire command bytes

Temperature encoding:
  - Types 0/2/3 combined VOLT_TEMP read: raw value / 100 → °C (BMS internal)
  - Types 0/2/3 dedicated TEMP_CMD:      raw uint16 / 10 - 273.15 → °C (1/10 K)
  - Type 5 (F0513):                       raw uint16 / 10 - 273.15 → °C (1/10 K)
  - Type 6:                               (-40*raw + 9323) / 100 → °C
"""

from PySide6.QtWidgets import (
    QApplication,
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QPushButton, QTreeWidget, QTreeWidgetItem,
    QLabel, QMessageBox, QHeaderView, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush

# ──────────────────────────────────────────────────────────────────────────────
# Universal commands  (all battery types)
# ──────────────────────────────────────────────────────────────────────────────

# cc aa 00  →  32-byte basic info (ROM ID, cycle count, lock state, capacity…)
READ_MSG_CMD = [0x01, 0x02, 0x28, 0x33, 0xAA, 0x00]

# ──────────────────────────────────────────────────────────────────────────────
# Battery type detection probes  (BTC04 probing sequence)
# ──────────────────────────────────────────────────────────────────────────────
TYPE0_PROBE_CMD = [0x01, 0x01, 0x10, 0xCC, 0xDC, 0x0B]
TYPE2_PROBE_CMD = [0x01, 0x01, 0x10, 0xCC, 0xDC, 0x0A]
TYPE3_PROBE_CMD = [0x01, 0x03, 0x02, 0xCC, 0xD4, 0x2C, 0x00, 0x02]
# Type 5 (F0513): ROM ID byte 3 < 100  (from basic_info response)
# Type 6 (BL36):  basic_info response byte 17 == 30

# ──────────────────────────────────────────────────────────────────────────────
# Types 0 / 2 / 3 — shared commands
# ──────────────────────────────────────────────────────────────────────────────
# cc dc 0c → 16-byte model string
MODEL_CMD = [0x01, 0x02, 0x10, 0xCC, 0xDC, 0x0C]
CHARGER_CMD = [0x01, 0x02, 0x20, 0xCC, 0xF0, 0x00]   # enter charger mode
READ_DATA_REQUEST = [0x01, 0x04, 0x1D, 0xCC,
                     0xD7, 0x00, 0x00, 0xFF]  # volt+temp combined
CLEAR_CMD = [0x01, 0x02, 0x00, 0xCC, 0xF0, 0x00]   # clear (no response)
# commit to flash (no response)
STORE_CMD = [0x01, 0x02, 0x00, 0x33, 0x55, 0xA5]
TESTMODE_CMD = [0x01, 0x03, 0x09, 0x33, 0xD9, 0x96, 0xA5]
TESTMODE_EXIT_CMD = [0x01, 0x03, 0x09, 0xCC, 0xD9, 0xFF, 0xFF]
LEDS_ON_CMD = [0x01, 0x02, 0x09, 0x33, 0xDA, 0x31]
LEDS_OFF_CMD = [0x01, 0x02, 0x09, 0x33, 0xDA, 0x34]
RESET_ERROR_CMD = [0x01, 0x02, 0x09, 0x33, 0xDA, 0x04]

# cc d7 19 00 04  →  int32 charge level + 0x06  (type 0 only)
CHARGE_LEVEL_CMD = [0x01, 0x04, 0x04, 0xCC, 0xD7, 0x19, 0x00, 0x04]

# Health registers (type-specific)
HEALTH_T0_CMD = [0x01, 0x03, 0x02, 0xCC, 0xD4, 0x50, 0x01, 0x02]
HEALTH_T2_CMD = [0x01, 0x03, 0x02, 0xCC, 0xD6, 0x04, 0x05, 0x02]
HEALTH_T3_CMD = [0x01, 0x03, 0x02, 0xCC, 0xD6, 0x38, 0x02, 0x02]

# Overdischarge counters (type-specific)
OVERDIS_T0_CMD = [0x01, 0x03, 0x01, 0xCC, 0xD4, 0xBA, 0x00, 0x01]
OVERDIS_T2_CMD = [0x01, 0x03, 0x01, 0xCC, 0xD6, 0x8D, 0x05, 0x01]
OVERDIS_T3_CMD = [0x01, 0x03, 0x01, 0xCC, 0xD6, 0x09, 0x03, 0x01]

# Overload counters (type-specific)
OVERLOAD_T0_CMD = [0x01, 0x03, 0x07, 0xCC, 0xD4, 0x8D, 0x00, 0x07]
OVERLOAD_T2_CMD = [0x01, 0x03, 0x07, 0xCC, 0xD6, 0x5F, 0x05, 0x07]
OVERLOAD_T3_CMD = [0x01, 0x03, 0x06, 0xCC, 0xD6, 0x5B, 0x03, 0x04]

# Reset battery message — write clean 32-byte frame, zero error nibble
# Based on original OBI-1 source (清理幀命令 / CLEAN_FRAME_CMD)
CLEAN_FRAME_CMD = [
    0x01, 0x22, 0x00,
    0x33, 0x0F, 0x00,
    0xF1, 0x26, 0xBD, 0x13, 0x14, 0x58, 0x00, 0x00,
    0x94, 0x94, 0x40, 0x21, 0xD0, 0x80, 0x02, 0x4E,
    0x23, 0xD0, 0x8E, 0x45, 0x60, 0x1A, 0x00, 0x03,
    0x02, 0x02, 0x0E, 0x20, 0x00, 0x30, 0x01, 0x83,
]

# ──────────────────────────────────────────────────────────────────────────────
# Type 5 (F0513) commands
# ──────────────────────────────────────────────────────────────────────────────
F0513_VCELL_CMDS = [
    [0x01, 0x01, 0x02, 0xCC, 0x31],
    [0x01, 0x01, 0x02, 0xCC, 0x32],
    [0x01, 0x01, 0x02, 0xCC, 0x33],
    [0x01, 0x01, 0x02, 0xCC, 0x34],
    [0x01, 0x01, 0x02, 0xCC, 0x35],
]
F0513_TEMP_CMD = [0x01, 0x01, 0x02, 0xCC, 0x52]
F0513_MODEL_CMD = [0x01, 0x00, 0x02, 0x31]
F0513_VERSION_CMD = [0x01, 0x00, 0x02, 0x32]
F0513_TESTMODE_CMD = [0x01, 0x01, 0x00, 0xCC, 0x99]

# ──────────────────────────────────────────────────────────────────────────────
# Type 6 (10-cell BL36xx)
# ──────────────────────────────────────────────────────────────────────────────
TYPE6_ENTER_CMD = [0x01, 0x02, 0x00, 0xCC, 0x10, 0x21]
TYPE6_DATA_CMD = [0x01, 0x01, 0x14, 0xCC, 0xD4]

# ──────────────────────────────────────────────────────────────────────────────
# Initial data table — defines display order for all rows
# ──────────────────────────────────────────────────────────────────────────────
INITIAL_DATA: dict[str, str] = {
    "Model":                    "",
    "Battery Type":             "",
    "Capacity":                 "",
    "Charge count*":            "",
    "State":                    "",
    "Status code":              "",
    "Manufacturing date":       "",
    "State of Charge":          "",
    "Health":                   "",
    "Pack Voltage":             "",
    "Cell 1 Voltage":           "",
    "Cell 2 Voltage":           "",
    "Cell 3 Voltage":           "",
    "Cell 4 Voltage":           "",
    "Cell 5 Voltage":           "",
    "Cell 6 Voltage":           "",
    "Cell 7 Voltage":           "",
    "Cell 8 Voltage":           "",
    "Cell 9 Voltage":           "",
    "Cell 10 Voltage":          "",
    "Cell Voltage Difference":  "",
    "Temperature Sensor 1":     "",
    "Temperature Sensor 2":     "",
    "Overdischarge count":      "",
    "Overdischarge %":          "",
    "Overload count":           "",
    "Overload %":               "",
    "ROM ID":                   "",
    "Battery message":          "",
}

ROW_EVEN = QColor("#1C1F26")
ROW_ODD = QColor("#20242C")

HEALTH_LABELS = {4: "Excellent", 3: "Good", 2: "Fair", 1: "Poor", 0: "Bad"}
SOC_LABELS = {7: "Full", 6: "High", 5: "Good", 4: "Medium",
                 3: "Low", 2: "Very Low", 1: "Critical", 0: "Empty"}


def get_display_name() -> str:
    return "Makita LXT"


# ──────────────────────────────────────────────────────────────────────────────
class ModuleApplication(QWidget):

    def __init__(self, parent=None, interface_module=None, obi_instance=None):
        super().__init__(parent)
        self.interface = None
        self.obi_instance = obi_instance
        self.battery_type: int | None = None
        self._capacity_raw: int = 0
        self._cycle_count:  int = 0
        self._basic_info_response = None

        self._build_ui()
        self._insert_battery_data(INITIAL_DATA)

    # ── public ────────────────────────────────────────────────────────────────

    def set_interface(self, interface_instance):
        self.interface = interface_instance
        # Keep all buttons disabled until the interface signals it is ready
        # (i.e. firmware version has been read after the Arduino boot delay).
        if hasattr(interface_instance, 'ready'):
            interface_instance.ready.connect(self._on_interface_ready)
        if hasattr(interface_instance, 'disconnected'):
            interface_instance.disconnected.connect(
                self._on_interface_disconnected)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        title = QLabel(get_display_name())
        title.setStyleSheet(
            "font-size: 18pt; font-weight: 700; color: #00B4CC; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel(
            "Li-ion Battery Diagnostics  ·  Types 0 / 2 / 3 / 5 / 6")
        subtitle.setStyleSheet(
            "font-size: 9pt; color: #3E4555; letter-spacing: 1px;")
        subtitle.setAlignment(Qt.AlignCenter)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #2E3340; margin: 2px 0;")

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(divider)
        root.addWidget(self._build_button_row())
        root.addWidget(self._build_tree(), stretch=1)
        root.addLayout(self._build_bottom_bar())

    def _build_button_row(self) -> QWidget:
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(10)
        grid.setContentsMargins(0, 0, 0, 0)

        rg = QGroupBox("Read Data")
        rl = QVBoxLayout(rg)
        rl.setContentsMargins(10, 18, 10, 10)
        self.btn_read_model = QPushButton("Read Battery Model")
        self.btn_read_data = QPushButton("Read Battery Data")
        # enabled once interface is ready
        self.btn_read_model.setEnabled(False)
        self.btn_read_data.setEnabled(False)
        for b in (self.btn_read_model, self.btn_read_data):
            rl.addWidget(b)
        self.btn_read_model.clicked.connect(self._on_read_static_click)
        self.btn_read_data.clicked.connect(self._on_read_data_click)

        fg = QGroupBox("Function Test")
        fl = QVBoxLayout(fg)
        fl.setContentsMargins(10, 18, 10, 10)
        self.btn_leds_on = QPushButton("LED Test  ON")
        self.btn_leds_off = QPushButton("LED Test  OFF")
        for b in (self.btn_leds_on, self.btn_leds_off):
            b.setEnabled(False)
            fl.addWidget(b)
        self.btn_leds_on.clicked.connect(self._on_leds_on)
        self.btn_leds_off.clicked.connect(self._on_leds_off)

        rsg = QGroupBox("Reset Battery")
        rsl = QVBoxLayout(rsg)
        rsl.setContentsMargins(10, 18, 10, 10)
        self.btn_clear_errors = QPushButton("Clear Errors")
        self.btn_reset_message = QPushButton("Reset Battery Message")
        for b in (self.btn_clear_errors, self.btn_reset_message):
            b.setEnabled(False)
            rsl.addWidget(b)
        self.btn_clear_errors.clicked.connect(self._on_reset_errors)
        self.btn_reset_message.clicked.connect(self._on_reset_message)

        grid.addWidget(rg,  0, 0)
        grid.addWidget(fg,  0, 1)
        grid.addWidget(rsg, 0, 2)

        # All action buttons start disabled; enabled via _on_interface_ready
        self._action_buttons = [
            self.btn_read_model,
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
        self.tree.setAlternatingRowColors(False)
        self.tree.setRootIsDecorated(False)
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        return self.tree

    def _build_bottom_bar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 4, 0, 0)
        note = QLabel(
            "* Charge count approximate  ·  Select rows then Copy to export")
        note.setStyleSheet("font-size: 8pt; color: #3E4555;")
        layout.addWidget(note, stretch=1)
        copy_btn = QPushButton("Copy Selected")
        copy_btn.setFixedWidth(110)
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedWidth(80)
        copy_btn.clicked.connect(self._copy_to_clipboard)
        clear_btn.clicked.connect(self._clear_data)
        layout.addWidget(copy_btn)
        layout.addWidget(clear_btn)
        return layout

    # ── helpers ───────────────────────────────────────────────────────────────

    def _enable_action_buttons(self, include_leds: bool = True,
                               include_reset: bool = True):
        self.btn_read_data.setEnabled(True)
        self.btn_leds_on.setEnabled(include_leds)
        self.btn_leds_off.setEnabled(include_leds)
        self.btn_clear_errors.setEnabled(include_reset)
        self.btn_reset_message.setEnabled(include_reset)

    def _disable_action_buttons(self):
        for b in self._action_buttons:
            b.setEnabled(False)

    def _require_interface(self) -> bool:
        if not self.interface:
            QMessageBox.critical(self, "No Interface",
                                 "Please connect an interface first.")
            return False
        return True

    def _log(self, msg: str):
        if self.obi_instance:
            self.obi_instance.update_debug(msg)

    @staticmethod
    def _nibble_swap(byte: int) -> int:
        return ((byte & 0xF0) >> 4) | ((byte & 0x0F) << 4)

    @staticmethod
    def _fmt_v(v: float) -> str:
        return f"{v:.3f} V"

    @staticmethod
    def _kelvin_tenth_to_celsius(raw: int) -> str:
        """uint16 in 1/10 Kelvin → Celsius.  e.g. 2965 → 23.35 °C"""
        return f"{raw / 10.0 - 273.15:.2f} °C"

    @staticmethod
    def _type6_byte_to_celsius(raw: int) -> str:
        """Type 6 single-byte temperature: t = (−40x + 9323) / 100"""
        return f"{(-40 * raw + 9323) / 100.0:.2f} °C"

    # ── type detection ────────────────────────────────────────────────────────

    def _detect_type(self, basic_info: bytes) -> int:
        """
        Identify battery type following the BTC04 probing sequence.
        Returns 0, 2, 3, 5, or 6.  Raises RuntimeError if unrecognised.
        """
        if len(basic_info) > 17 and basic_info[17] == 30:
            return 6

        if len(basic_info) > 5 and basic_info[5] < 100:
            return 5

        try:
            r = self.interface.request(TYPE0_PROBE_CMD)
            if r and r[-1] == 0x06:
                return 0
        except Exception as e:
            self._log(f"[TYPE-DET] Type-0 probe: {e}")

        try:
            self.interface.request(TYPE2_PROBE_CMD)
            return 2
        except Exception as e:
            self._log(f"[TYPE-DET] Type-2 probe: {e}")

        try:
            self.interface.request(TYPE3_PROBE_CMD)
            return 3
        except Exception as e:
            self._log(f"[TYPE-DET] Type-3 probe: {e}")

        raise RuntimeError("Battery present but type could not be determined.")

    # ── model probes ──────────────────────────────────────────────────────────

    def _try_get_model_standard(self) -> str | None:
        try:
            r = self.interface.request(MODEL_CMD)
            model = r[2:18].decode(
                "utf-8", errors="replace").rstrip("\x00").strip()
            return model or None
        except Exception as e:
            self._log(f"[MODEL] Standard probe failed: {e}")
            return None

    def _try_get_f0513_model(self) -> str | None:
        try:
            r = self.interface.request(F0513_MODEL_CMD)
            self.interface.request(CLEAR_CMD)
            return f"BL{r[2]:X}{r[3]:X}"
        except Exception as e:
            self._log(f"[MODEL] F0513 probe failed: {e}")
            return None

    # ── interface readiness ───────────────────────────────────────────────────

    def _on_interface_ready(self):
        """Called when the interface has finished its boot sequence and is ready."""
        self.btn_read_model.setEnabled(True)

    def _on_interface_disconnected(self):
        """Called when the interface disconnects — disable all action buttons."""
        for b in self._action_buttons:
            b.setEnabled(False)

    # ── main button handlers ──────────────────────────────────────────────────

    def _on_read_static_click(self):
        if not self._require_interface():
            return

        try:
            response = self.interface.request(READ_MSG_CMD)
            self._basic_info_response = response
        except ConnectionError as e:
            QMessageBox.critical(self, "Connection Error",
                                 f"Could not communicate with the battery:\n\n{e}")
            return
        except (IndexError, ValueError) as e:
            QMessageBox.critical(self, "Data Error",
                                 f"Received an unexpected response while reading battery info:\n\n{type(e).__name__}: {e}")
            return
        except Exception as e:
            QMessageBox.critical(self, "Read Error",
                                 f"Failed to read battery static data:\n\n{type(e).__name__}: {e}")
            return

        # Parse static fields from basic_info response
        # Byte layout from original OBI source + rosvall protocol docs:
        #   [2]     mfg year  (nibble-swapped BCD)
        #   [3]     mfg month (nibble-swapped BCD)
        #   [4]     mfg day   (nibble-swapped BCD)
        #   [2:10]  ROM ID
        #   [10:42] raw battery message (32 bytes)
        #   [21]    hardware type byte
        #   [26]    capacity (nibble-swapped, in tenths of Ah)
        #   [29]    status / error code
        #   [30]    lock nibble (lower 4 bits)
        #   [36:38] charge count bytes (nibble-swapped)
        swapped = bytearray([self._nibble_swap(response[39]),
                             self._nibble_swap(response[38])])[::-1]
        cycle_count = int.from_bytes(swapped, "big") & 0x0FFF
        self._cycle_count = cycle_count

        lock_nibble = response[30] & 0x0F
        lock_status = "LOCKED" if lock_nibble > 0 else "UNLOCKED"

        cap_raw = self._nibble_swap(response[26])
        self._capacity_raw = cap_raw

        # Date is stored as plain BCD in ROM ID bytes [2:5], no nibble swap needed.
        # ROM ID example: 16 06 12 64 ... → year=0x16=22dec → 2016?, no:
        # 0x16 = 22 decimal but treated as BCD → year 16 → 2016
        # Actually the bytes ARE the BCD values directly: 0x16 → year 16, 0x06 → month 6, 0x12 → day 12
        mfg_year = response[2]   # e.g. 0x16 = year 2016
        mfg_month = response[3]   # e.g. 0x06 = June
        mfg_day = response[4]   # e.g. 0x12 = 12th

        self._insert_battery_data({
            "ROM ID":             " ".join(f"{b:02X}" for b in response[2:10]),
            "Battery message":    " ".join(f"{b:02X}" for b in response[10:42]),
            "Charge count*":      cycle_count,
            "State":              lock_status,
            "Status code":        f"{response[29]:02X}",
            "Manufacturing date": f"{mfg_day:02d}/{mfg_month:02d}/20{mfg_year:02d}",
            "Capacity":           f"{cap_raw / 10:.1f} Ah",
        })

        try:
            btype = self._detect_type(response)
        except RuntimeError as e:
            QMessageBox.critical(self, "Unsupported Battery", str(e))
            return

        self.battery_type = btype
        self._log(f"[DETECT] Battery type: {btype}")

        type_labels = {
            0: "Type 0 — Standard (newest)",
            2: "Type 2",
            3: "Type 3",
            5: "Type 5 — F0513 MCU",
            6: "Type 6 — 10-cell BL36xx",
        }
        self._insert_battery_data(
            {"Battery Type": type_labels.get(btype, str(btype))})

        model = self._try_get_model_standard() or self._try_get_f0513_model()
        self._insert_battery_data({"Model": model or "Unknown"})

        # F0513 supports voltage/temp only, no LED test or reset commands
        if btype == 5:
            self._enable_action_buttons(
                include_leds=False, include_reset=False)
        else:
            self._enable_action_buttons()

    def _on_read_data_click(self):
        if not self._require_interface():
            return
        try:
            if self.battery_type == 5:
                self._read_data_type5()
            elif self.battery_type == 6:
                self._read_data_type6()
            else:
                self._read_data_standard()
        except ConnectionError as e:
            QMessageBox.critical(self, "Connection Error",
                                 f"Lost communication while reading battery data:\n\n{e}")
        except (IndexError, ValueError) as e:
            QMessageBox.critical(self, "Data Error",
                                 f"Received an unexpected response while reading battery data:\n\n{type(e).__name__}: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Read Error",
                                 f"Failed to read battery data:\n\n{type(e).__name__}: {e}")

    # ── per-type data readers ─────────────────────────────────────────────────

    def _read_data_standard(self):
        """Types 0/2/3: combined voltage+temp, then type-specific extras."""
        r = self.interface.request(READ_DATA_REQUEST)

        v_pack = int.from_bytes(r[2:4],   "little") / 1000
        voltages = [int.from_bytes(r[i:i+2], "little") / 1000
                    for i in range(4, 14, 2)]
        t1 = int.from_bytes(r[16:18], "little") / 100   # °C×100 from BMS
        t2 = int.from_bytes(r[18:20], "little") / 100

        data: dict = {
            "Pack Voltage":            self._fmt_v(v_pack),
            "Cell 1 Voltage":          self._fmt_v(voltages[0]),
            "Cell 2 Voltage":          self._fmt_v(voltages[1]),
            "Cell 3 Voltage":          self._fmt_v(voltages[2]),
            "Cell 4 Voltage":          self._fmt_v(voltages[3]),
            "Cell 5 Voltage":          self._fmt_v(voltages[4]),
            "Cell Voltage Difference": self._fmt_v(
                round(max(voltages) - min(voltages), 3)),
            "Temperature Sensor 1":    f"{t1:.2f} °C",
            "Temperature Sensor 2":    f"{t2:.2f} °C",
        }

        if self.battery_type == 0:
            try:
                cl_r = self.interface.request(CHARGE_LEVEL_CMD)
                charge_level = int.from_bytes(cl_r[2:6], "little")
                soc = self._calc_soc(charge_level)
                data["State of Charge"] = f"{soc}/7  ({SOC_LABELS.get(soc, '')})"
            except Exception as e:
                self._log(f"[WARN] SoC: {e}")

            try:
                h_r = self.interface.request(HEALTH_T0_CMD)
                h_raw = int.from_bytes(h_r[2:4], "little")
                h = self._calc_health_t0(h_raw)
                data["Health"] = f"{h:.1f}/4  ({HEALTH_LABELS.get(round(h), '')})"
            except Exception as e:
                self._log(f"[WARN] Health T0: {e}")

            try:
                od_r = self.interface.request(OVERDIS_T0_CMD)
                ol_r = self.interface.request(OVERLOAD_T0_CMD)
                data.update(self._fmt_overload_stats(od_r[2], list(ol_r[2:9])))
            except Exception as e:
                self._log(f"[WARN] Overload T0: {e}")

        elif self.battery_type == 2:
            try:
                od_r = self.interface.request(OVERDIS_T2_CMD)
                ol_r = self.interface.request(OVERLOAD_T2_CMD)
                h_r = self.interface.request(HEALTH_T2_CMD)
                od = od_r[2]
                ol = list(ol_r[2:9])
                h_raw = int.from_bytes(h_r[2:4], "little")
                h = self._calc_health_generic(od, ol)
                data["Health"] = f"{h:.1f}/4  ({HEALTH_LABELS.get(round(h), '')})"
                data.update(self._fmt_overload_stats(od, ol))
            except Exception as e:
                self._log(f"[WARN] Stats T2: {e}")

        elif self.battery_type == 3:
            try:
                od_r = self.interface.request(OVERDIS_T3_CMD)
                ol_r = self.interface.request(OVERLOAD_T3_CMD)
                h_r = self.interface.request(HEALTH_T3_CMD)
                od = od_r[2]
                ol = list(ol_r[2:8])
                h = self._calc_health_generic(od, ol)
                data["Health"] = f"{h:.1f}/4  ({HEALTH_LABELS.get(round(h), '')})"
                data.update(self._fmt_overload_stats(od, ol))
            except Exception as e:
                self._log(f"[WARN] Stats T3: {e}")

        self._insert_battery_data(data)

    def _read_data_type5(self):
        """F0513: clear twice, read 5 cells individually, then temperature."""
        self.interface.request(CLEAR_CMD)
        self.interface.request(CLEAR_CMD)

        voltages = []
        for cmd in F0513_VCELL_CMDS:
            r = self.interface.request(cmd)
            voltages.append(int.from_bytes(r[2:4], "little") / 1000)

        t_r = self.interface.request(F0513_TEMP_CMD)
        t_raw = int.from_bytes(t_r[2:4], "little")

        self._insert_battery_data({
            "Pack Voltage":            self._fmt_v(round(sum(voltages), 3)),
            "Cell 1 Voltage":          self._fmt_v(voltages[0]),
            "Cell 2 Voltage":          self._fmt_v(voltages[1]),
            "Cell 3 Voltage":          self._fmt_v(voltages[2]),
            "Cell 4 Voltage":          self._fmt_v(voltages[3]),
            "Cell 5 Voltage":          self._fmt_v(voltages[4]),
            "Cell Voltage Difference": self._fmt_v(
                round(max(voltages) - min(voltages), 3)),
            "Temperature Sensor 1":    self._kelvin_tenth_to_celsius(t_raw),
            "Temperature Sensor 2":    "",
        })

    def _read_data_type6(self):
        """Type 6 (10-cell BL36xx): enter second command panel, read 20 bytes."""
        self.interface.request(TYPE6_ENTER_CMD)
        r = self.interface.request(TYPE6_DATA_CMD)

        voltages = [int.from_bytes(r[2+i*2:4+i*2], "little") / 1000
                    for i in range(10)]
        t_raw = r[22] if len(r) > 22 else 0

        data: dict = {
            "Pack Voltage":            self._fmt_v(round(sum(voltages), 3)),
            "Temperature Sensor 1":    self._type6_byte_to_celsius(t_raw),
            "Temperature Sensor 2":    "",
            "Cell Voltage Difference": self._fmt_v(
                round(max(voltages) - min(voltages), 3)),
        }
        for i, v in enumerate(voltages, 1):
            data[f"Cell {i} Voltage"] = self._fmt_v(v)
        self._insert_battery_data(data)

    # ── BTC04 calculations ────────────────────────────────────────────────────

    def _calc_soc(self, charge_level: int) -> int:
        """State of charge 0–7  (BTC04 formula)."""
        cap = self._capacity_raw
        if cap == 0:
            return 0
        ratio = charge_level / cap / 2880
        if ratio == 0:
            return 0
        elif ratio < 10:
            return 1
        else:
            return min(int(ratio / 10), 7)

    def _calc_health_t0(self, health_raw: int) -> float:
        """Type 0 hardware health → 0–4 scale  (BTC04 formula)."""
        cap = self._capacity_raw
        if cap == 0:
            return 0.0
        ratio = health_raw / cap
        return 4.0 if ratio > 80 else max(0.0, ratio / 10 - 5)

    def _calc_health_generic(self, overdischarge: int,
                             overload_counters: list) -> float:
        """Types 2/3 health → 0–4 scale  (BTC04 formula)."""
        cap = self._capacity_raw
        cycles = self._cycle_count
        f_ol = max(sum(overload_counters) - 29, 0)
        f_od = max(35 - overdischarge, 0)
        dmg = cycles + cycles * (f_ol + f_od) / 32
        scale = 1000 if cap in (26, 28, 40, 50) else 600
        return max(0.0, 4.0 - dmg / scale)

    def _fmt_overload_stats(self, overdischarge: int,
                            overload_counters: list) -> dict:
        # 0xFF is a sentinel meaning "not applicable / no data" on some battery types
        if overdischarge == 0xFF:
            overdischarge = 0
        overload_counters = [0 if c == 0xFF else c for c in overload_counters]
        cycles = self._cycle_count
        ol_sum = sum(overload_counters)
        od_pct = (round(4 + 100 * overdischarge / cycles, 1)
                  if overdischarge > 0 and cycles > 0 else 0)
        ol_pct = (round(4 + 100 * ol_sum / cycles, 1)
                  if ol_sum > 0 and cycles > 0 else 0)
        return {
            "Overdischarge count": overdischarge,
            "Overdischarge %":     f"{od_pct} %",
            "Overload count":      ol_sum,
            "Overload %":          f"{ol_pct} %",
        }

    # ── LED / function-test handlers ──────────────────────────────────────────

    def _on_leds_on(self):
        if not self._require_interface():
            return
        try:
            self.interface.request(TESTMODE_CMD)
            self.interface.request(LEDS_ON_CMD)
            self._log("[LED] LEDs ON")
        except ConnectionError as e:
            QMessageBox.critical(self, "Connection Error",
                                 f"Lost communication while turning LEDs on:\n\n{e}")
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"LED ON failed:\n\n{type(e).__name__}: {e}")

    def _on_leds_off(self):
        if not self._require_interface():
            return
        try:
            self.interface.request(TESTMODE_CMD)
            self.interface.request(LEDS_OFF_CMD)
            self._log("[LED] LEDs OFF")
        except ConnectionError as e:
            QMessageBox.critical(self, "Connection Error",
                                 f"Lost communication while turning LEDs off:\n\n{e}")
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"LED OFF failed:\n\n{type(e).__name__}: {e}")

    def _on_reset_errors(self):
        if not self._require_interface():
            return
        try:
            self.interface.request(TESTMODE_CMD)
            self.interface.request(RESET_ERROR_CMD)
            self._log("[RESET] Error flags cleared")
            QMessageBox.information(self, "Done", "Error flags cleared.")
        except ConnectionError as e:
            QMessageBox.critical(self, "Connection Error",
                                 f"Lost communication while resetting errors:\n\n{e}")
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Clear errors failed:\n\n{type(e).__name__}: {e}")

    def _on_reset_message(self):
        """
        Write clean 32-byte frame to battery to reset the stored error state.
        Requires user confirmation — this is a flash-write operation.

        ⚠ Only use after physically resolving the fault.
        """
        if not self._require_interface():
            return

        confirm = QMessageBox.question(
            self, "Reset Battery Message",
            "This writes a clean frame to the battery to clear the error state.\n\n"
            "Only proceed after the fault has been physically repaired.\n\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            self.interface.request(CHARGER_CMD)
            self.interface.request(CLEAN_FRAME_CMD)
            self.interface.request(STORE_CMD)
            self._log(
                "[RESET] Battery message reset — clean frame written to flash")
            QMessageBox.information(
                self, "Done",
                "Battery message reset.\n\n"
                "Disconnect the battery for 10 seconds before reconnecting.",
            )
        except ConnectionError as e:
            QMessageBox.critical(self, "Connection Error",
                                 f"Lost communication while resetting battery message:\n\n{e}")
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Reset message failed:\n\n{type(e).__name__}: {e}")

    # ── tree ──────────────────────────────────────────────────────────────────

    def _insert_battery_data(self, data: dict):
        for parameter, value in data.items():
            items = self.tree.findItems(parameter, Qt.MatchExactly, 0)
            if items:
                items[0].setText(1, str(value))
            else:
                row = self.tree.topLevelItemCount()
                item = QTreeWidgetItem([parameter, str(value)])
                col = ROW_EVEN if row % 2 == 0 else ROW_ODD
                for c in range(2):
                    item.setBackground(c, QBrush(col))
                item.setForeground(0, QBrush(QColor("#7A8499")))
                self.tree.addTopLevelItem(item)

    def _copy_to_clipboard(self):
        selected = self.tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Nothing Selected",
                                "Select one or more rows first.")
            return
        lines = [f"{i.text(0)}\t{i.text(1)}" for i in selected]
        QApplication.clipboard().setText("\n".join(lines))
        QMessageBox.information(self, "Copied",
                                f"{len(lines)} row(s) copied to clipboard.")

    def _clear_data(self):
        self._insert_battery_data(INITIAL_DATA)
        self.battery_type = None
        self._capacity_raw = 0
        self._cycle_count = 0
        self._basic_info_response = None
        self._disable_action_buttons()
