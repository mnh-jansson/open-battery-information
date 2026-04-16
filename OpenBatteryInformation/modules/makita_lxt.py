"""
makita_lxt.py  —  Makita LXT 18V battery diagnostics module for OBI-1.

Supports battery types: 0 (standard/newest), 2, 3, 5 (F0513), 6 (10-cell BL36xx).
Detects and reports unsupported pre-type-0 BMS hardware (all-0xFF basic info).

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

import csv
import json
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication,
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QPushButton, QTreeWidget, QTreeWidgetItem,
    QLabel, QMessageBox, QHeaderView, QFrame, QFileDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush

# ──────────────────────────────────────────────────────────────────────────────
# Provenance markers for command constants
# confirmed    — MCU firmware dumped and reverse-engineered (most reliable)
# inferred     — derived from BTC04/DC18RC traces or protocol documentation
# dangerous    — writes to flash/memory, requires caution
# persistent   — changes are written to battery flash storage
# ──────────────────────────────────────────────────────────────────────────────
# [provenance] Universal commands (all battery types)
# cc aa 00  →  32-byte basic info (ROM ID, cycle count, lock state, capacity…) [confirmed]
READ_MSG_CMD = [0x01, 0x02, 0x28, 0x33, 0xAA, 0x00]

# [provenance] Battery type detection probes (BTC04 probing sequence) [inferred]
TYPE0_PROBE_CMD = [0x01, 0x01, 0x10, 0xCC, 0xDC, 0x0B]
TYPE2_PROBE_CMD = [0x01, 0x01, 0x10, 0xCC, 0xDC, 0x0A]
TYPE3_PROBE_CMD = [0x01, 0x03, 0x02, 0xCC, 0xD4, 0x2C, 0x00, 0x02]

# [provenance] Types 0/2/3 shared commands [confirmed]
MODEL_CMD = [0x01, 0x02, 0x10, 0xCC, 0xDC,
             0x0C]      # cc dc 0c → 16-byte model
# enter charger mode [confirmed]
CHARGER_CMD = [0x01, 0x02, 0x20, 0xCC, 0xF0, 0x00]
READ_DATA_REQUEST = [0x01, 0x04, 0x1D, 0xCC,          # volt+temp combined
                     0xD7, 0x00, 0x00, 0xFF]
# clear (no response) [confirmed]
CLEAR_CMD = [0x01, 0x02, 0x00, 0xCC, 0xF0, 0x00]
# commit to flash [confirmed][persistent]
STORE_CMD = [0x01, 0x02, 0x00, 0x33, 0x55, 0xA5]
TESTMODE_CMD = [0x01, 0x03, 0x09, 0x33, 0xD9,
                0x96, 0xA5]  # enter test mode [confirmed]
TESTMODE_EXIT_CMD = [0x01, 0x03, 0x09, 0xCC, 0xD9,
                     0xFF, 0xFF]  # exit test mode [confirmed]
LEDS_ON_CMD = [0x01, 0x02, 0x09, 0x33, 0xDA, 0x31]   # LED test ON [inferred]
LEDS_OFF_CMD = [0x01, 0x02, 0x09, 0x33, 0xDA, 0x34]  # LED test OFF [inferred]
# clear error flags [confirmed]
RESET_ERROR_CMD = [0x01, 0x02, 0x09, 0x33, 0xDA, 0x04]

# [provenance] Type 0 only [confirmed]
CHARGE_LEVEL_CMD = [0x01, 0x04, 0x04, 0xCC,
                    0xD7, 0x19, 0x00, 0x04]  # int32 charge level

# [provenance] Health registers [inferred]
HEALTH_T0_CMD = [0x01, 0x03, 0x02, 0xCC, 0xD4, 0x50, 0x01, 0x02]  # 2 bytes
HEALTH_T2_CMD = [0x01, 0x03, 0x02, 0xCC, 0xD6, 0x04, 0x05, 0x02]  # 2 bytes
HEALTH_T3_CMD = [0x01, 0x03, 0x06, 0xCC, 0xD6, 0x38,
                 0x02, 0x02]  # 6 bytes (fixed per done.land)

# [provenance] Overdischarge counters [inferred]
OVERDIS_T0_CMD = [0x01, 0x03, 0x01, 0xCC, 0xD4, 0xBA, 0x00, 0x01]  # 1 byte
OVERDIS_T2_CMD = [0x01, 0x03, 0x02, 0xCC,
                  0xD6, 0x8D, 0x05, 0x01]  # 2 bytes (fixed)
OVERDIS_T3_CMD = [0x01, 0x03, 0x02, 0xCC, 0xD6, 0x09,
                  0x03, 0x01]  # 2 bytes (fixed per done.land)

# [provenance] Overload counters [inferred]
OVERLOAD_T0_CMD = [0x01, 0x03, 0x07, 0xCC, 0xD4, 0x8D, 0x00, 0x07]  # 7 bytes
OVERLOAD_T2_CMD = [0x01, 0x03, 0x07, 0xCC, 0xD6, 0x5F, 0x05, 0x07]  # 7 bytes
OVERLOAD_T3_CMD = [0x01, 0x03, 0x06, 0xCC,
                   0xD6, 0x5B, 0x03, 0x04]  # 6 bytes (fixed)

# [provenance][dangerous][persistent] Reset battery message
# Based on original OBI-1 source (清理幀命令 / CLEAN_FRAME_CMD) [confirmed]
CLEAN_FRAME_CMD = [
    0x01, 0x22, 0x00,
    0x33, 0x0F, 0x00,
    0xF1, 0x26, 0xBD, 0x13, 0x14, 0x58, 0x00, 0x00,
    0x94, 0x94, 0x40, 0x21, 0xD0, 0x80, 0x02, 0x4E,
    0x23, 0xD0, 0x8E, 0x45, 0x60, 0x1A, 0x00, 0x03,
    0x02, 0x02, 0x0E, 0x20, 0x00, 0x30, 0x01, 0x83,
]

# [provenance] Type 5 (F0513) commands
# Per rosvall/makita-lxt-protocol/type5.md:
#   Cell voltages: bare commands 0x31..0x35 (NO 0xCC prefix) → 2 bytes each
#   Temperature:   cc 52 → 2 bytes, little-endian int16 in 1/10 K
# Frame write_len follows the (wire_bytes - 1) convention used by the
# Arduino firmware for other commands in this file.
F0513_VCELL_CMDS = [
    [0x01, 0x00, 0x02, 0x31],   # cell 1
    [0x01, 0x00, 0x02, 0x32],   # cell 2
    [0x01, 0x00, 0x02, 0x33],   # cell 3
    [0x01, 0x00, 0x02, 0x34],   # cell 4
    [0x01, 0x00, 0x02, 0x35],   # cell 5
]
F0513_TEMP_CMD = [0x01, 0x01, 0x02, 0xCC, 0x52]  # temperature
# F0513 model / firmware live in the temporary second command tree.
# Martin Jansson documents main-panel 0x99 as the gate into that tree,
# after which 0x31 returns the 2-byte battery model and 0x32 the
# 2-byte firmware version.
F0513_MODEL_CMD = [0x01, 0x00, 0x02, 0x31]
F0513_VERSION_CMD = [0x01, 0x00, 0x02, 0x32]
F0513_SECOND_TREE_CMD = [0x01, 0x01, 0x00, 0xCC, 0x99]

# [provenance] Type 6 (10-cell BL36xx)
# Per rosvall/makita-lxt-protocol/type6.md:
#   Enter state:    cc 10 21   (0 bytes response)
#   Cell voltages:  bare d4    (20 bytes, 10x int16 little-endian scaled)
#   Temperature:    bare d2    (1 byte)
# Voltage conversion:  v_mV = 6000 - (x / 10)    where x is the raw int16
# Temperature conversion:  t = (-40*x + 9323) / 100
TYPE6_ENTER_CMD = [0x01, 0x02, 0x00, 0xCC,
                   0x10, 0x21]  # enter 10-cell read state
TYPE6_DATA_CMD = [0x01, 0x00, 0x14, 0xD4]      # bare d4 → 20 bytes cell data
TYPE6_TEMP_CMD = [0x01, 0x00, 0x01, 0xD2]      # bare d2 → 1 byte temp

# ──────────────────────────────────────────────────────────────────────────────
# Capability table per battery type
# ──────────────────────────────────────────────────────────────────────────────
CAPABILITIES: dict[int, dict] = {
    0: {
        "name": "Type 0 — Standard (newest)",
        "mcu": "STM32L051 (confirmed) / RAJ240 (inferred)",
        "cells": 5,
        "supports_voltage": True,
        "supports_temp": True,
        "supports_soc": True,
        "supports_health": True,
        "supports_overload": True,
        "supports_overdischarge": True,
        "supports_leds": True,
        "supports_reset_errors": True,
        "supports_reset_message": True,
        "supports_model": True,
    },
    2: {
        "name": "Type 2",
        "mcu": "Unknown (inferred from BTC04 traces)",
        "cells": 5,
        "supports_voltage": True,
        "supports_temp": True,
        "supports_soc": False,
        "supports_health": True,
        "supports_overload": True,
        "supports_overdischarge": True,
        "supports_leds": True,
        "supports_reset_errors": True,
        "supports_reset_message": True,
        "supports_model": True,
    },
    3: {
        "name": "Type 3",
        "mcu": "Unknown (inferred from BTC04 traces)",
        "cells": 5,
        "supports_voltage": True,
        "supports_temp": True,
        "supports_soc": False,
        "supports_health": True,
        "supports_overload": True,
        "supports_overdischarge": True,
        "supports_leds": True,
        "supports_reset_errors": True,
        "supports_reset_message": True,
        "supports_model": True,
    },
    5: {
        "name": "Type 5 — F0513 MCU (experimental read-only)",
        "mcu": "NEC/Renesas F0513",
        "cells": 5,
        "supports_voltage": True,
        "supports_temp": True,
        "supports_soc": False,
        "supports_health": False,
        "supports_overload": False,
        "supports_overdischarge": False,
        "supports_leds": False,
        "supports_reset_errors": False,
        "supports_reset_message": False,
        "supports_model": True,
    },
    6: {
        "name": "Type 6 — 10-cell BL36xx",
        "mcu": "Unknown (inferred from field reports)",
        "cells": 10,
        "supports_voltage": True,
        "supports_temp": True,
        "supports_soc": False,
        "supports_health": False,
        "supports_overload": False,
        "supports_overdischarge": False,
        "supports_leds": False,
        "supports_reset_errors": False,
        "supports_reset_message": False,
        "supports_model": False,
    },
}

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

# ──────────────────────────────────────────────────────────────────────────────
# Known BMS boards  (from mnh-jansson/open-battery-information wiki + field reports)
# ──────────────────────────────────────────────────────────────────────────────
# Maps board family → dict with: mcu, voltage, supported, safe_to_charge, note
#
# IMPORTANT: MC908JK3E-based boards have NO cell monitoring or protection
# circuit implemented at all. They appear across multiple eras (2008–2012+)
# and BOTH voltage classes. Do not assume "old = unprotected, new = safe" —
# the board family matters, not the date. Field heuristic: packs with the
# Makita star mark on the label appear to always have a real BMS; packs
# without it (e.g. BL1415) appear to be the unprotected HC08 family.
#
# discovery_method values:
#   firmware_dump  — MCU firmware extracted and reverse-engineered (most reliable)
#   protocol_trace — derived from BTC04 / DC18RC traces (rosvall protocol docs)
#   field_report   — observed behavior from end-user testing
#   cross_reference — reported as working by independent forks (Belik1982, etc.)
#
# Hardware note: All authoritative sources (rosvall/makita-lxt-protocol,
# done.land, appositeit/obi-esp32) specify 4.7 kΩ pull-ups to 3.3–5 V on
# both the data line and the enable pin. Use those values.
KNOWN_BOARDS = {
    "MC908JK3E": {
        "mcu":    "Freescale HC08",
        "boards": "LIP5002 / LIPW001 (18V) / LIP4112 (14.4V, BL1415)",
        "voltage": "14.4V / 18V",
        "supported": False,
        "safe_to_charge": False,
        "discovery_method": "field_report",
        "note": ("No cell monitoring or protection circuit implemented. "
                 "Spans 2008–2012+ across both voltage classes. "
                 "DO NOT attempt to charge — unsafe regardless of pack age. "
                 "Field heuristic: missing Makita star mark on the label."),
    },
    "uPD78F0513": {
        "mcu":    "NEC/Renesas F0513",
        "boards": ("LIPW002/003/005/006/011/012/013 (18V) / "
                   "BL1820 unmarked PCB (18V)"),
        "voltage": "14.4V / 18V",
        "supported": False,
        "safe_to_charge": False,
        "discovery_method": "protocol_trace",
        "note": ("Type 5 — listed as NOT SUPPORTED in the upstream "
                 "mnh-jansson wiki. Firmware was partially dumped by "
                 "Martin Jansson (2021) but the full command set is "
                 "incomplete and no working reset procedure exists. "
                 "Cell-voltage and temperature reads may succeed on "
                 "unlocked packs, but this path is EXPERIMENTAL: write "
                 "operations (LEDs, clear errors, reset message) are "
                 "disabled because their effect on F0513 hardware is "
                 "not verified. Locked F0513 packs cannot be unlocked "
                 "with this tool — the only documented recovery path "
                 "is a UART backdoor (not implemented here)."),
    },
    "R2J240": {
        "mcu":    "Renesas RL78 (R2J240 / RAJ240 family)",
        "boards": ("BL1430-20 (14.4V, late 2011) / "
                   "RAJ240080DFP on BL1840B / BL1850B / BL1850B-D (18V)"),
        "voltage": "14.4V / 18V",
        "supported": True,
        "safe_to_charge": True,
        "discovery_method": "firmware_dump",
        "note": ("RL78-based, protected. Firmware dumped and analyzed by "
                 "mnh-jansson upstream. May be readable via type 0/2/3 "
                 "protocol path — needs validation. Used across both "
                 "voltage classes from late 2011 onwards."),
    },
    "MAK01": {
        "mcu":    "MAK01",
        "boards": "BL1815N / BL1820",
        "voltage": "18V",
        "supported": True,
        "safe_to_charge": True,
        "discovery_method": "firmware_dump",
        "note": "Supported upstream (mnh-jansson).",
    },
    "MAK02": {
        "mcu":    "MAK02",
        "boards": "LIPW014 / LIPW015",
        "voltage": "18V",
        "supported": True,
        "safe_to_charge": True,
        "discovery_method": "firmware_dump",
        "note": "Supported upstream (mnh-jansson).",
    },
    "STM32L051": {
        "mcu":    "ST STM32L051C8",
        "boards": "LIPW017",
        "voltage": "18V",
        "supported": True,
        "safe_to_charge": True,
        "discovery_method": "firmware_dump",
        "note": ("Supported upstream (mnh-jansson). This is the board where "
                 "the breakthrough happened — STM32 read protection was not "
                 "set, allowing full firmware analysis in Ghidra (2024)."),
    },
}

HEALTH_LABELS = {4: "Excellent", 3: "Good", 2: "Fair", 1: "Poor", 0: "Bad"}
SOC_LABELS = {7: "Full", 6: "High", 5: "Good", 4: "Medium",
                 3: "Low", 2: "Very Low", 1: "Critical", 0: "Empty"}


def get_display_name() -> str:
    return "Makita LXT"


# ──────────────────────────────────────────────────────────────────────────────
# Makita operation state machine
# Centralizes command sequencing for battery operations
# ──────────────────────────────────────────────────────────────────────────────

class MakitaOperation:
    IDLE = "idle"
    READING_BASIC_INFO = "reading_basic_info"
    DETECTING_TYPE = "detecting_type"
    READING_MODEL = "reading_model"
    READING_DATA = "reading_data"
    ERROR = "error"
    COMPLETE = "complete"


class MakitaCommandRunner:
    """
    Centralized command runner for Makita battery operations.
    Manages sequencing: read_basic_info -> detect_type -> read_model -> enable_actions.

    State transitions:
        IDLE -> READING_BASIC_INFO -> DETECTING_TYPE -> READING_MODEL -> COMPLETE
                                                      -> ERROR (if type detection fails)
    """

    def __init__(self, interface, log_cb, battery_type_cb=None):
        self.interface = interface
        self._log = log_cb
        self._on_battery_type_detected = battery_type_cb
        self._state = MakitaOperation.IDLE
        self._basic_info = None
        self._battery_type = None
        self._model = None
        self._error = None

    @property
    def state(self) -> str:
        return self._state

    @property
    def battery_type(self) -> int | None:
        return self._battery_type

    @property
    def basic_info(self) -> bytes | None:
        return self._basic_info

    @property
    def model(self) -> str | None:
        return self._model

    def reset(self):
        self._state = MakitaOperation.IDLE
        self._basic_info = None
        self._battery_type = None
        self._model = None
        self._error = None

    def read_basic_info(self) -> bytes:
        """
        Step 1: Read basic battery info (ROM ID, cycle count, lock state, capacity).
        Returns the response bytes.
        Raises ValueError if all-0xFF (unsupported BMS).
        """
        self._state = MakitaOperation.READING_BASIC_INFO
        self._log("[RUNNER] Step 1: Reading basic info")

        response = self.interface.request(
            READ_MSG_CMD,
            operation_name="READ_MSG",
            expected_length=40
        )

        if all(b == 0xFF for b in response[2:]):
            self._state = MakitaOperation.ERROR
            self._error = "All-0xFF response (unsupported pre-type-0 BMS)"
            raise ValueError("All-0xFF response (no data at this register)")

        self._basic_info = response
        self._log(f"[RUNNER] Basic info received: {len(response)} bytes")
        return response

    def detect_type(self, basic_info: bytes = None) -> int:
        """
        Step 2: Detect battery type (0, 2, 3, 5, or 6).
        Uses the basic_info if provided, otherwise reads it.
        Raises RuntimeError if type cannot be determined.
        """
        self._state = MakitaOperation.DETECTING_TYPE
        self._log("[RUNNER] Step 2: Detecting battery type")

        if basic_info is None and self._basic_info is None:
            basic_info = self.read_basic_info()
        elif basic_info is None:
            basic_info = self._basic_info

        if len(basic_info) >= 44:
            if basic_info[17] == 30:
                self._battery_type = 6
                self._log("[RUNNER] Type 6 detected: byte[17] == 30")
                return 6

            if basic_info[5] < 100:
                self._battery_type = 5
                self._log(
                    f"[RUNNER] Type 5 detected: byte[5] = {basic_info[5]} < 100")
                return 5

        try:
            r = self.interface.request(
                TYPE0_PROBE_CMD,
                operation_name="TYPE0_PROBE",
                expected_length=16,
                expected_bytes=[(15, 0x06)]
            )
            if r and len(r) >= 18 and r[-1] == 0x06:
                self._battery_type = 0
                self._log("[RUNNER] Type 0 confirmed: response[-1] == 0x06")
                return 0
        except Exception as e:
            self._log(f"[RUNNER] Type-0 probe failed: {e}")

        try:
            r = self.interface.request(
                TYPE2_PROBE_CMD,
                operation_name="TYPE2_PROBE",
                expected_length=16
            )
            if r and len(r) >= 18:
                self._battery_type = 2
                self._log("[RUNNER] Type 2 confirmed: probe responded")
                return 2
        except Exception as e:
            self._log(f"[RUNNER] Type-2 probe failed: {e}")
            try:
                self.interface.request(
                    TESTMODE_EXIT_CMD, operation_name="TESTMODE_EXIT")
                self._log(
                    "[RUNNER] Recovery: test-mode-exit sent after failed type 2 probe")
            except Exception as exit_e:
                self._log(
                    f"[RUNNER] Recovery failed: test-mode-exit error: {exit_e}")

        try:
            r = self.interface.request(
                TYPE3_PROBE_CMD,
                operation_name="TYPE3_PROBE",
                expected_length=2
            )
            if r and len(r) >= 4:
                self._battery_type = 3
                self._log("[RUNNER] Type 3 confirmed: probe responded")
                return 3
        except Exception as e:
            self._log(f"[RUNNER] Type-3 probe failed: {e}")

        self._state = MakitaOperation.ERROR
        self._error = "Battery present but type could not be determined"
        raise RuntimeError(self._error)

    def read_model(self, battery_type: int = None) -> str | None:
        """
        Step 3: Read battery model based on detected type.
        Returns the model string or None if unavailable.
        """
        self._state = MakitaOperation.READING_MODEL
        self._log("[RUNNER] Step 3: Reading battery model")

        if battery_type is None:
            battery_type = self._battery_type

        if battery_type == 5:
            try:
                self.interface.request(
                    F0513_SECOND_TREE_CMD,
                    operation_name="F0513_SECOND_TREE")
                r = self.interface.request(
                    F0513_MODEL_CMD, operation_name="MODEL_F0513")
                model = f"BL{r[3]:02X}{r[2]:02X}"
                self._model = model
                self._log(f"[RUNNER] Model (F0513): {model}")
                return model
            except Exception as e:
                self._log(f"[RUNNER] F0513 model read failed: {e}")
                return None
        else:
            try:
                r = self.interface.request(
                    MODEL_CMD, operation_name="MODEL_STD")
                model = r[2:18].decode(
                    "utf-8", errors="replace").rstrip("\x00").strip()
                if model:
                    self._model = model
                    self._log(f"[RUNNER] Model (standard): {model}")
                    return model
            except Exception as e:
                self._log(f"[RUNNER] Standard model read failed: {e}")
            return None

    def run_full_sequence(self) -> dict:
        """
        Run the complete battery read sequence.
        Returns a dict with: basic_info, battery_type, model, error.
        """
        self.reset()
        result = {
            "basic_info": None,
            "battery_type": None,
            "model": None,
            "error": None
        }

        try:
            result["basic_info"] = self.read_basic_info()
        except ValueError as e:
            result["error"] = str(e)
            self._log(f"[RUNNER] Basic info read failed: {e}")
            return result

        try:
            result["battery_type"] = self.detect_type()
        except RuntimeError as e:
            result["error"] = str(e)
            self._log(f"[RUNNER] Type detection failed: {e}")
            return result

        result["model"] = self.read_model()

        self._state = MakitaOperation.COMPLETE
        self._log("[RUNNER] Full sequence complete")
        return result


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
        if self.interface is not None:
            if hasattr(self.interface, 'ready'):
                try:
                    self.interface.ready.disconnect(self._on_interface_ready)
                except RuntimeError:
                    pass
            if hasattr(self.interface, 'disconnected'):
                try:
                    self.interface.disconnected.disconnect(
                        self._on_interface_disconnected)
                except RuntimeError:
                    pass

        self.interface = interface_instance
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
            "Li-ion Battery Diagnostics · Types 0/2/3 (full) · Type 5 (experimental) · Pre-type-0 detection"
        )
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
            "* Charge count approximate")
        note.setStyleSheet("font-size: 8pt; color: #3E4555;")
        layout.addWidget(note, stretch=1)

        copy_btn = QPushButton("Copy")
        copy_btn.setMinimumWidth(80)
        copy_btn.clicked.connect(self._copy_to_clipboard)
        layout.addWidget(copy_btn)

        export_csv_btn = QPushButton("Export CSV")
        export_csv_btn.setMinimumWidth(100)
        export_csv_btn.clicked.connect(self._export_csv)
        layout.addWidget(export_csv_btn)

        export_json_btn = QPushButton("Export JSON")
        export_json_btn.setMinimumWidth(100)
        export_json_btn.clicked.connect(self._export_json)
        layout.addWidget(export_json_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setMinimumWidth(80)
        clear_btn.clicked.connect(self._clear_data)
        layout.addWidget(clear_btn)
        return layout

    # ── helpers ───────────────────────────────────────────────────────────────

    def _enable_action_buttons(self, leds: bool = True,
                               reset_errors: bool = True,
                               reset_message: bool = True,
                               read_data: bool = True):
        self.btn_read_data.setEnabled(read_data)
        self.btn_leds_on.setEnabled(leds)
        self.btn_leds_off.setEnabled(leds)
        self.btn_clear_errors.setEnabled(reset_errors)
        self.btn_reset_message.setEnabled(reset_message)

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
    def _bcd_decode(byte: int) -> int:
        """Decode a BCD byte to its decimal value.
        0x16 -> 16, 0x06 -> 6, 0x12 -> 12.
        Returns -1 if either nybble is an invalid BCD digit (>9)."""
        hi = (byte >> 4) & 0x0F
        lo = byte & 0x0F
        if hi > 9 or lo > 9:
            return -1
        return hi * 10 + lo

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

        Type detection uses multiple validation levels:
        1. Byte position matches (weakest - can give false positives)
        2. Probe command response length validation
        3. Probe response byte validation

        WARNING: the type 2 probe command (cc dc 0a) has the documented
        side effect of enabling test mode on the battery. If a type 2 probe
        fails on a non-type-2 battery, the battery may be left in test mode
        with checksums that no longer validate, causing the DC18RC charger
        to refuse it. We send an explicit test-mode-exit (cc d9 ff ff)
        after a failed type 2 probe to restore the battery to a known-good state.
        """
        if len(basic_info) >= 44:
            if basic_info[17] == 30:
                self._log("[TYPE-DET] Type 6 detected: byte[17] == 30")
                return 6

            if basic_info[5] < 100:
                self._log(
                    f"[TYPE-DET] Type 5 detected: byte[5] = {basic_info[5]} < 100")
                return 5

        try:
            r = self.interface.request(
                TYPE0_PROBE_CMD,
                operation_name="TYPE0_PROBE",
                expected_length=16,
                expected_bytes=[(15, 0x06)])
            if r and len(r) >= 18 and r[-1] == 0x06:
                self._log("[TYPE-DET] Type 0 confirmed: response[-1] == 0x06")
                return 0
        except Exception as e:
            self._log(f"[TYPE-DET] Type-0 probe failed: {e}")

        try:
            r = self.interface.request(
                TYPE2_PROBE_CMD,
                operation_name="TYPE2_PROBE",
                expected_length=16)
            if r and len(r) >= 18 and not all(b == 0xFF for b in r[2:]):
                self._log("[TYPE-DET] Type 2 confirmed: probe responded")
                return 2
        except Exception as e:
            self._log(f"[TYPE-DET] Type-2 probe failed: {e}")
            try:
                self.interface.request(
                    TESTMODE_EXIT_CMD, operation_name="TESTMODE_EXIT")
                self._log(
                    "[TYPE-DET] Recovery: test-mode-exit sent after failed type 2 probe")
            except Exception as exit_e:
                self._log(
                    f"[TYPE-DET] Recovery failed: test-mode-exit error: {exit_e}")

        try:
            r = self.interface.request(
                TYPE3_PROBE_CMD,
                operation_name="TYPE3_PROBE",
                expected_length=2)
            if r and len(r) >= 4 and not all(b == 0xFF for b in r[2:]):
                self._log("[TYPE-DET] Type 3 confirmed: probe responded")
                return 3
        except Exception as e:
            self._log(f"[TYPE-DET] Type-3 probe failed: {e}")

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
            self.interface.request(
                F0513_SECOND_TREE_CMD,
                operation_name="F0513_SECOND_TREE")
            r = self.interface.request(
                F0513_MODEL_CMD,
                operation_name="MODEL_F0513")
            model = f"BL{r[3]:02X}{r[2]:02X}"

            try:
                self.interface.request(
                    F0513_SECOND_TREE_CMD,
                    operation_name="F0513_SECOND_TREE")
                fw = self.interface.request(
                    F0513_VERSION_CMD,
                    operation_name="FW_F0513")
                self._log(
                    "[MODEL] F0513 firmware: "
                    f"{fw[3]:02X}.{fw[2]:02X}"
                )
            except Exception as fw_e:
                self._log(f"[MODEL] F0513 firmware probe failed: {fw_e}")

            return model
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

    # ── pre-type-0 safety dialog ──────────────────────────────────────────────

    def _show_pre_type0_safety_dialog(self):
        """
        Surface the MC908JK3E unprotected-BMS safety warning.
        Called from _on_read_static_click when the basic info read returns
        all-0xFF, either via a worker-raised ValueError or via a direct
        check on the response bytes.
        """
        board = KNOWN_BOARDS["MC908JK3E"]
        self._log("[DETECT] Basic info response is all 0xFF "
                  f"— matches {board['mcu']} ({board['boards']})")
        self._insert_battery_data({
            "Battery Type":    f"Unsupported — {board['mcu']}",
            "Battery message": "FF FF FF FF (all bytes 0xFF)",
        })
        QMessageBox.critical(
            self, "⚠ Unsafe BMS — Do Not Charge",
            f"This battery uses a {board['mcu']} board.\n\n"
            f"Known boards in this family:\n  {board['boards']}\n\n"
            f"{board['note']}\n\n"
            "These boards have no overdischarge, overcurrent, or "
            "per-cell protection. The cells will work in a tool but "
            "MUST NOT be charged on any charger — including older "
            "DC18RA models. Charging unprotected lithium cells is a "
            "serious fire/explosion risk.\n\n"
            "Field check: packs without the Makita star mark on the "
            "label appear to always be this unprotected family.\n\n"
            "Recommendation: retire the pack or swap the BMS board "
            "for a newer protected one (F0513, MAK01/02, RL78, STM32).",
        )

    # ── main button handlers ──────────────────────────────────────────────────

    def _on_read_static_click(self):
        if not self._require_interface():
            return

        self._log("[READ] Reading basic info...")
        self.btn_read_model.setEnabled(False)
        QApplication.processEvents()

        # Wrap the entire read in try/finally so btn_read_model is guaranteed
        # to be re-enabled on exit, regardless of which return path is taken
        # (pre-type-0 dialog, unsupported battery error, or normal completion).
        # Without this, every early return would leave the user stranded with
        # no way to re-read without first pressing Clear.
        try:
            self._do_read_static()
        finally:
            self.btn_read_model.setEnabled(True)

    def _do_read_static(self):
        try:
            response = self.interface.request(
                READ_MSG_CMD, operation_name="READ_MSG")
            self._basic_info_response = response
        except Exception as e:
            # The all-FF case is a legitimate "unsupported pre-type-0 BMS"
            # signal, not a communication error. The worker converts all-FF
            # into a ValueError with a known message; catch that specifically
            # and surface the safety dialog instead of the generic read error.
            if "All-0xFF" in str(e):
                self._show_pre_type0_safety_dialog()
                return
            QMessageBox.critical(self, "Read Error",
                                 f"Failed to read battery info:\n{e}")
            return

        # ── Early bail-out for pre-type-0 BMS hardware ────────────────────
        # Belt-and-braces: if the worker *didn't* raise (e.g. max_attempts
        # was set high enough that one attempt got non-FF garbage through),
        # still check for an all-FF payload here before parsing any fields.
        if all(b == 0xFF for b in response[2:]):
            self._show_pre_type0_safety_dialog()
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
        battery_is_locked = lock_nibble > 0

        cap_raw = self._nibble_swap(response[26])
        self._capacity_raw = cap_raw

        # Manufacturing date: first three ROM ID bytes interpreted as raw
        # decimal (year, month, day). This field is not documented in any
        # authoritative Makita protocol spec — this is the convention used by
        # the upstream mnh-jansson/open-battery-information tool, and matches
        # real-world purchase dates better than a BCD interpretation.
        mfg_year = response[2]
        mfg_month = response[3]
        mfg_day = response[4]

        mfg_date_str = f"{mfg_day:02d}/{mfg_month:02d}/20{mfg_year:02d}"

        self._insert_battery_data({
            "ROM ID":             " ".join(f"{b:02X}" for b in response[2:10]),
            "Battery message":    " ".join(f"{b:02X}" for b in response[10:42]),
            "Charge count*":      cycle_count,
            "State":              lock_status,
            "Status code":        f"{response[29]:02X}",
            "Manufacturing date": mfg_date_str,
            "Capacity":           f"{cap_raw / 10:.1f} Ah",
        })

        try:
            btype = self._detect_type(response)
        except RuntimeError as e:
            QMessageBox.critical(self, "Unsupported Battery", str(e))
            return

        self.battery_type = btype
        self._log(f"[DETECT] Battery type: {btype}")

        cap = CAPABILITIES.get(btype, CAPABILITIES.get(0))
        self._insert_battery_data(
            {"Battery Type": cap.get("name", str(btype))})

        if btype == 5:
            model = self._try_get_f0513_model()
        elif cap.get("supports_model", False):
            model = self._try_get_model_standard()
        else:
            model = None
        self._insert_battery_data({"Model": model or "Unknown"})

        self._enable_action_buttons(
            leds=cap.get("supports_leds", True),
            reset_errors=cap.get("supports_reset_errors", True),
            reset_message=cap.get("supports_reset_message", True),
            read_data=True)

        # Type 5 (F0513) — surface experimental-status notice.
        # Upstream mnh-jansson wiki lists all uPD78F0513-based boards as
        # NOT SUPPORTED. Reads may work on unlocked packs but write
        # operations are not validated and are disabled via CAPABILITIES.
        if btype == 5:
            board = KNOWN_BOARDS.get("uPD78F0513", {})
            self._log(
                "[INFO] Type 5 (F0513) detected — experimental read-only path")
            QMessageBox.information(
                self, "Type 5 (F0513) — Experimental",
                "This battery uses an NEC/Renesas uPD78F0513 BMS.\n\n"
                "Upstream Open Battery Information lists this board "
                "family as NOT SUPPORTED. OBI-1 will attempt to read "
                "cell voltages, pack voltage, and temperature, but:\n\n"
                "  • Health, SoC, and overload counters are unavailable\n"
                "  • LED test, Clear Errors, and Reset Message are disabled\n"
                "  • Locked F0513 packs cannot be unlocked with this tool\n\n"
                "Read values should be treated as indicative only and "
                "cross-checked with a multimeter before making any "
                "decision about the pack."
            )

        # If the battery came back locked, warn the user about common
        # field "repair" methods that destroy safety. The Hackaday/Makita
        # repair forums frequently recommend jumpering across the BMS
        # protection MOSFETs to bypass a locked state — this works
        # mechanically but eliminates ALL overcurrent and overvoltage
        # protection, leaving an unprotected lithium pack.
        if battery_is_locked:
            self._log("[WARN] Battery reports LOCKED state — surfacing "
                      "FET-jumper safety warning")
            QMessageBox.warning(
                self, "Battery Locked",
                "This battery is currently in a LOCKED state.\n\n"
                "Try the 'Clear Errors' or 'Reset Battery Message' "
                "functions first — many lockouts are software faults "
                "that can be cleared safely.\n\n"
                "⚠ DO NOT jumper across the BMS protection MOSFETs.\n\n"
                "This is a commonly recommended 'fix' on repair forums "
                "and YouTube, and it does work mechanically — but it "
                "permanently disables ALL overcurrent, overdischarge, "
                "and short-circuit protection. The pack will work in "
                "tools but becomes a fire/explosion risk during charging "
                "or under fault conditions. If software unlock fails, "
                "the correct repair is replacing the BMS board, not "
                "bypassing it.",
            )

    def _on_read_data_click(self):
        if not self._require_interface():
            return

        self._log(f"[READ] Reading data (type {self.battery_type})...")
        self.btn_read_data.setEnabled(False)
        QApplication.processEvents()

        try:
            if self.battery_type == 5:
                self._read_data_type5()
            elif self.battery_type == 6:
                self._read_data_type6()
            else:
                self._read_data_standard()
            self._log("[READ] Data read complete")
        except Exception as e:
            QMessageBox.critical(self, "Read Error",
                                 f"Failed to read battery data:\n{e}")
        finally:
            self.btn_read_data.setEnabled(True)

    # ── per-type data readers ─────────────────────────────────────────────────

    def _read_data_standard(self):
        """Types 0/2/3: combined voltage+temp, then type-specific extras."""
        r = self.interface.request(READ_DATA_REQUEST)

        v_pack = int.from_bytes(r[2:4],   "little") / 1000
        voltages = [int.from_bytes(r[i:i+2], "little") / 1000
                    for i in range(4, 14, 2)]
        t1 = int.from_bytes(r[16:18], "little") / 100
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
        """Type 6 (10-cell BL36xx): enter read state, read 20-byte cell data,
        then separately read 1-byte temperature.

        Per rosvall/makita-lxt-protocol/type6.md:
          - cc 10 21  → enter state (0 bytes response)
          - bare d4   → 20 bytes (10x int16 LE, scaled/offset cell voltages)
          - bare d2   → 1 byte  (temperature)

        Cell voltage decode:  v_mV = 6000 - (raw_int16 / 10)
        Temperature decode:   t_C  = (-40 * raw_byte + 9323) / 100
        """
        self.interface.request(TYPE6_ENTER_CMD)
        r = self.interface.request(TYPE6_DATA_CMD)

        # 10 cells × 2 bytes each = 20 bytes, starting at r[2] after framing
        raws = [int.from_bytes(r[2 + i * 2:4 + i * 2], "little")
                for i in range(10)]
        voltages = [(6000 - raw / 10.0) / 1000.0 for raw in raws]

        # Temperature is a separate command on type 6, not appended to the
        # voltage response. Reading r[22] (old behaviour) was out of bounds
        # and silently produced ~93 °C from raw=0.
        try:
            t_r = self.interface.request(TYPE6_TEMP_CMD)
            t_raw = t_r[2]
            temp_str = self._type6_byte_to_celsius(t_raw)
        except Exception as e:
            self._log(f"[WARN] Type 6 temperature read failed: {e}")
            temp_str = "—"

        data: dict = {
            "Pack Voltage":            self._fmt_v(round(sum(voltages), 3)),
            "Temperature Sensor 1":    temp_str,
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
        """Type 0 hardware health → 0–4 scale  (BTC04 formula: ratio = health / cap)."""
        cap = self._capacity_raw
        if cap == 0:
            return 0.0
        ratio = health_raw / cap
        return 4.0 if ratio > 80 else max(0.0, ratio / 10.0 - 5)

    def _calc_health_generic(self, overdischarge: int,
                             overload_counters: list) -> float:
        """Types 2/3 health → 0–4 scale  (BTC04 formula)."""
        cap = self._capacity_raw
        cycles = self._cycle_count
        if cycles == 0:
            return 0.0
        f_ol = max(sum(overload_counters) - 29, 0)
        f_od = max(35 - overdischarge, 0)
        dmg = cycles + cycles * float(f_ol + f_od) / 32.0
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

    def _capability_allows(self, capability_key: str, op_name: str) -> bool:
        """Gate write operations at handler level in addition to button state.
        Returns True if the current battery type supports the operation.
        Shows an informational dialog and returns False otherwise.
        Belt-and-braces: buttons are already disabled via _enable_action_buttons
        based on CAPABILITIES, but this prevents any accidental re-enable from
        issuing a write command to a battery whose firmware response to that
        command is not documented."""
        cap = CAPABILITIES.get(self.battery_type, {})
        if cap.get(capability_key, False):
            return True
        btype_name = cap.get("name", f"Type {self.battery_type}")
        self._log(f"[GUARD] {op_name} blocked — not supported on {btype_name}")
        QMessageBox.information(
            self, f"{op_name} not supported",
            f"The {op_name} operation is not supported on:\n"
            f"  {btype_name}\n\n"
            "This is not a bug. The command's effect on this BMS "
            "family is either undocumented or confirmed to differ "
            "from the Type 0/2/3 behaviour, and issuing it blindly "
            "could leave the battery in an inconsistent state."
        )
        return False

    def _on_leds_on(self):
        if not self._require_interface():
            return
        if not self._capability_allows("supports_leds", "LED test"):
            return
        try:
            self.interface.request(TESTMODE_CMD)
            self.interface.request(LEDS_ON_CMD)
            self._log("[LED] LEDs ON")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"LED ON failed:\n{e}")

    def _on_leds_off(self):
        if not self._require_interface():
            return
        if not self._capability_allows("supports_leds", "LED test"):
            return
        try:
            self.interface.request(TESTMODE_CMD)
            self.interface.request(LEDS_OFF_CMD)
            self._log("[LED] LEDs OFF")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"LED OFF failed:\n{e}")

    def _on_reset_errors(self):
        if not self._require_interface():
            return
        if not self._capability_allows("supports_reset_errors", "Clear Errors"):
            return
        try:
            self.interface.request(TESTMODE_CMD)
            self.interface.request(RESET_ERROR_CMD)
            self._log("[RESET] Error flags cleared")
            QMessageBox.information(self, "Done", "Error flags cleared.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Clear errors failed:\n{e}")

    def _on_reset_message(self):
        """
        Write clean 32-byte frame to battery to reset the stored error state.
        Requires user confirmation — this is a [dangerous][persistent] operation.

        ⚠ Only use after physically resolving the fault.
        """
        if not self._require_interface():
            return
        if not self._capability_allows("supports_reset_message",
                                       "Reset Battery Message"):
            return

        cap = CAPABILITIES.get(self.battery_type, {})
        btype_name = cap.get("name", f"Type {self.battery_type}")
        mcu_info = cap.get("mcu", "Unknown MCU")

        lock_status = "LOCKED"
        items = self.tree.findItems("State", Qt.MatchExactly, 0)
        if items:
            lock_status = items[0].text(1)

        warning_msg = (
            f"⚠ DESTRUCTIVE OPERATION — FLASH WRITE\n\n"
            f"Battery Type: {btype_name}\n"
            f"MCU: {mcu_info}\n"
            f"Lock State: {lock_status}\n\n"
            f"This operation will:\n"
            f"  1. Enter charger mode\n"
            f"  2. Write a clean 32-byte frame to battery flash\n"
            f"  3. Commit changes to persistent storage\n\n"
            f"⚠ PERSISTENT: Changes survive battery removal.\n\n"
            f"Only proceed if:\n"
            f"  • The underlying fault has been physically repaired\n"
            f"  • Cells are at safe voltage levels\n"
            f"  • You understand this modifies battery data\n\n"
            f"Continue?"
        )

        confirm = QMessageBox.warning(
            self, "⚠ Reset Battery Message — FLASH WRITE",
            warning_msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            self._log("[RESET] Battery message reset cancelled by user")
            return

        try:
            self.interface.request(CHARGER_CMD, operation_name="RESET_CHARGER")
            self.interface.request(
                CLEAN_FRAME_CMD, operation_name="RESET_CLEAN_FRAME")
            self.interface.request(STORE_CMD, operation_name="RESET_STORE")
            self._log(
                "[RESET] Battery message reset — clean frame written to flash")
            QMessageBox.information(
                self, "Done",
                "Battery message reset.\n\n"
                "Disconnect the battery for 10 seconds before reconnecting.",
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Reset message failed:\n{e}")

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

    def _get_battery_data(self) -> dict:
        """Collect all battery data from the tree as a dictionary."""
        data = {}
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            data[item.text(0)] = item.text(1)
        return data

    def _export_csv(self):
        data = self._get_battery_data()
        if not data:
            QMessageBox.warning(self, "No Data",
                                "No battery data to export.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"battery_data_{timestamp}.csv"

        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", default_name,
            "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return

        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Parameter", "Value"])
                for param, value in data.items():
                    writer.writerow([param, value])
            self._log(f"[EXPORT] CSV exported: {path}")
            QMessageBox.information(self, "Exported",
                                    f"Data exported to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error",
                                 f"Failed to export CSV:\n{e}")

    def _export_json(self):
        data = self._get_battery_data()
        if not data:
            QMessageBox.warning(self, "No Data",
                                "No battery data to export.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"battery_data_{timestamp}.json"

        path, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", default_name,
            "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return

        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "app_version": "OBI-1 v1.0.0",
                "battery_data": data
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            self._log(f"[EXPORT] JSON exported: {path}")
            QMessageBox.information(self, "Exported",
                                    f"Data exported to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error",
                                 f"Failed to export JSON:\n{e}")

    def _clear_data(self):
        self._insert_battery_data(INITIAL_DATA)
        self.battery_type = None
        self._capacity_raw = 0
        self._cycle_count = 0
        self._basic_info_response = None
        self._disable_action_buttons()
        # If the interface is still connected, re-enable Read Battery Model
        # so the user can immediately start a fresh read after clearing.
        # Without this, Clear leaves the user stranded with no way to begin
        # a new read short of disconnecting and reconnecting the interface.
        if self.interface is not None and getattr(
                self.interface, 'serial', None) is not None and \
                self.interface.serial.is_open:
            self.btn_read_model.setEnabled(True)
