import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QComboBox, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
import serial
import serial.tools.list_ports

INTERFACE_VERSION_CMD = [0x01, 0x00, 0x03, 0x01]
DEFAULT_BAUD_RATE = 9600


def get_display_name():
    return "Arduino OBI"


def _execute_serial(serial_port: serial.Serial, request: list,
                    max_attempts: int, debug_cb,
                    operation_name: str = None,
                    battery_type: int = None,
                    expected_length: int = None,
                    expected_bytes: list = None):
    """
    Unified serial execution logic for both sync and async paths.

    Args:
        serial_port: Open serial connection
        request: Command bytes to send
        max_attempts: Number of retry attempts
        debug_cb: Debug logging callback
        operation_name: Human-readable operation name for logging
        battery_type: Battery type if known (for logging)
        expected_length: Expected response payload length (for validation)
        expected_bytes: Expected byte values at specific positions

    Returns:
        Response bytes or None for fire-and-forget commands

    Raises:
        Exception on failure after all retries
    """
    if not serial_port.is_open:
        raise Exception("Serial port is not open.")

    if expected_length is None:
        expected_length = request[2]

    for attempt in range(1, max_attempts + 1):
        start_time = time.perf_counter()
        payload_hex = ' '.join(f'{x:02X}' for x in request[3:])

        log_prefix = ""
        if operation_name:
            log_prefix += f"[{operation_name}]"
        if battery_type is not None:
            log_prefix += f" T{battery_type}"
        log_prefix += f" #{attempt}/{max_attempts}"

        debug_cb(f"{log_prefix} TX {payload_hex} ({len(request)} bytes)")

        try:
            serial_port.reset_input_buffer()
            serial_port.write(bytearray(request))

            response = serial_port.read(expected_length + 2)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            if len(response) < 2:
                debug_cb(f"{log_prefix} TIMEOUT (got {len(response)} bytes, "
                         f"expected {expected_length + 2}, {elapsed_ms:.1f}ms)")
                continue

            response_hex = ' '.join(f'{x:02X}' for x in response[2:])
            debug_cb(f"{log_prefix} RX {response_hex} ({len(response)} bytes, "
                     f"{elapsed_ms:.1f}ms)")

            if expected_length == 0:
                return None

            if len(response) != expected_length + 2:
                debug_cb(f"{log_prefix} LEN_MISMATCH: got {len(response)}, "
                         f"expected {expected_length + 2}")
                continue

            payload = response[2:]

            # "No data at this register" signatures. All three shapes below
            # have been observed from real hardware when a Type 0/2/3 command
            # is sent to a BMS that doesn't implement that register:
            #   1. all bytes 0xFF            — classic "register empty"
            #   2. all bytes 0x00            — observed on some Type 3 packs
            #   3. 0xFF followed by all 0x00 — observed on misclassified packs
            #      where the first byte is the 1-wire terminator echo leaking
            #      into the payload and the rest is zeroed out
            # A payload of length 1 is too short to distinguish signal from
            # noise, so skip this check for single-byte responses.
            if len(payload) >= 2:
                all_ff = all(b == 0xFF for b in payload)
                all_zero = all(b == 0x00 for b in payload)
                ff_then_zeros = (payload[0] == 0xFF
                                 and all(b == 0x00 for b in payload[1:]))

                if all_ff:
                    debug_cb(
                        f"{log_prefix} ALL_0xFF (no data at this register)")
                    raise ValueError(
                        "All-0xFF response (no data at this register)")
                if all_zero:
                    debug_cb(
                        f"{log_prefix} ALL_0x00 (no data at this register)")
                    raise ValueError(
                        "All-0x00 response (no data at this register)")
                if ff_then_zeros:
                    debug_cb(f"{log_prefix} FF_THEN_ZEROS "
                             f"(no data at this register)")
                    raise ValueError(
                        "FF-then-zeros response (no data at this register)")

            if expected_bytes:
                mismatch = False
                for pos, expected in expected_bytes:
                    if pos < len(payload) and payload[pos] != expected:
                        debug_cb(f"{log_prefix} BYTE_MISMATCH at [{pos}]: "
                                 f"got 0x{payload[pos]:02X}, expected 0x{expected:02X}")
                        mismatch = True
                        break
                if mismatch:
                    continue

            return response

        except ValueError:
            raise
        except Exception as e:
            debug_cb(f"{log_prefix} TRANSPORT_ERROR: {type(e).__name__}: {e}")

    raise Exception(f"No valid response after {max_attempts} attempts.")


class _SerialWorker(QObject):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, serial_port: serial.Serial, request: list,
                 max_attempts: int, debug_cb, operation_name: str = None,
                 battery_type: int = None, expected_length: int = None,
                 expected_bytes: list = None):
        super().__init__()
        self._serial = serial_port
        self._request = request
        self._max_attempts = max_attempts
        self._debug = debug_cb
        self._operation_name = operation_name
        self._battery_type = battery_type
        self._expected_length = expected_length
        self._expected_bytes = expected_bytes

    def run(self):
        try:
            self.finished.emit(self._execute())
        except Exception as e:
            self.error.emit(str(e))

    def _execute(self):
        return _execute_serial(
            self._serial, self._request, self._max_attempts, self._debug,
            self._operation_name, self._battery_type,
            self._expected_length, self._expected_bytes)


class Interface(QWidget):
    ready = Signal()
    disconnected = Signal()
    connected = Signal()

    def __init__(self, parent, obi_instance):
        super().__init__(parent)
        self.obi_instance = obi_instance
        self.serial = serial.Serial()
        self.serial.timeout = 1
        self._threads: list[QThread] = []
        self._connected_signals: bool = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(self._small_label("Serial Port"))
        self.port_combo = QComboBox()
        self.port_combo.addItems(self._get_ports())
        layout.addWidget(self.port_combo)

        layout.addSpacing(4)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setProperty("accent", True)
        self.connect_btn.setStyle(self.connect_btn.style())
        self.connect_btn.clicked.connect(self._toggle_connection)
        layout.addWidget(self.connect_btn)

        refresh_btn = QPushButton("Refresh Ports")
        refresh_btn.clicked.connect(self._refresh_ports)
        layout.addWidget(refresh_btn)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #2E3340;")
        layout.addWidget(line)

        self.version_label = QLabel("Firmware: —")
        self.version_label.setStyleSheet("color: #5A9E6F; font-size: 9pt;")
        layout.addWidget(self.version_label)

    @staticmethod
    def _small_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 8pt; color: #5A6070; font-weight: 600; "
                          "letter-spacing: 0.5px; text-transform: uppercase;")
        return lbl

    def _get_ports(self) -> list[str]:
        return [p.device for p in serial.tools.list_ports.comports()]

    def _refresh_ports(self):
        current = self.port_combo.currentText()
        ports = self._get_ports()
        self.port_combo.clear()
        self.port_combo.addItems(ports)
        if current in ports:
            self.port_combo.setCurrentText(current)

    def _set_controls_enabled(self, enabled: bool):
        self.port_combo.setEnabled(enabled)
        self.connect_btn.setEnabled(enabled)

    def _toggle_connection(self):
        if self.serial.is_open:
            self._close()
        else:
            self._open()

    def _open(self):
        port = self.port_combo.currentText()
        if not port:
            self.obi_instance.update_debug("[WARN] No serial port selected.")
            return

        available = self._get_ports()
        if port not in available:
            self.obi_instance.update_debug(
                f"[WARN] Port {port} not found. Available: {available or 'none'}"
            )
            self._refresh_ports()
            return

        self.serial.port = port
        self.serial.baudrate = DEFAULT_BAUD_RATE
        try:
            self.serial.open()
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setProperty("accent", False)
            self.connect_btn.setProperty("danger", True)
            self.connect_btn.style().unpolish(self.connect_btn)
            self.connect_btn.style().polish(self.connect_btn)
            self.obi_instance.update_debug(
                f"[INFO] Opened {port} @ {self.serial.baudrate:,} baud"
            )
            self._update_version_async()
            self.connected.emit()
        except Exception as e:
            self.serial.close()
            self.obi_instance.update_debug(f"[ERROR] Cannot open {port}: {e}")

    def _close(self):
        if self.serial.is_open:
            self.serial.close()
        self.connect_btn.setText("Connect")
        self.connect_btn.setProperty("danger", False)
        self.connect_btn.setProperty("accent", True)
        self.connect_btn.style().unpolish(self.connect_btn)
        self.connect_btn.style().polish(self.connect_btn)
        self.connect_btn.setEnabled(True)
        self.port_combo.setEnabled(True)
        self.version_label.setText("Firmware: —")
        self.obi_instance.update_debug("[INFO] Serial port closed.")
        self.disconnected.emit()

    def _update_version_async(self):
        self._set_controls_enabled(False)

        def on_done(response):
            if response:
                version = '.'.join(str(b) for b in response[2:])
                self.version_label.setText(f"Firmware: {version}")
            self._set_controls_enabled(True)
            self.ready.emit()

        def on_error(msg):
            self.version_label.setText("Firmware: error")
            self.obi_instance.update_debug(
                f"[WARN] Version read failed: {msg}")
            self._set_controls_enabled(True)
            self.ready.emit()

        self._run_async(INTERFACE_VERSION_CMD, max_attempts=5,
                        operation_name="FW_VER",
                        on_finished=on_done, on_error=on_error)

    def _run_async(self, request: list, max_attempts: int = 2,
                   operation_name: str = None, battery_type: int = None,
                   expected_length: int = None, expected_bytes: list = None,
                   on_finished=None, on_error=None):
        thread = QThread()
        worker = _SerialWorker(
            self.serial, request, max_attempts,
            self.obi_instance.update_debug, operation_name,
            battery_type, expected_length, expected_bytes)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)

        if on_finished:
            worker.finished.connect(on_finished)
        if on_error:
            worker.error.connect(on_error)

        def _cleanup():
            if thread in self._threads:
                self._threads.remove(thread)
            worker.deleteLater()

        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(_cleanup)

        self._threads.append(thread)
        thread.start()

    def request_async(self, request: list, max_attempts: int = 2,
                      operation_name: str = None, battery_type: int = None,
                      expected_length: int = None, expected_bytes: list = None,
                      on_finished=None, on_error=None):
        self._run_async(request, max_attempts, operation_name,
                        battery_type, expected_length, expected_bytes,
                        on_finished, on_error)

    def request(self, request: list, max_attempts: int = 2,
                operation_name: str = None, battery_type: int = None,
                expected_length: int = None, expected_bytes: list = None):
        return _execute_serial(
            self.serial, request, max_attempts,
            self.obi_instance.update_debug, operation_name,
            battery_type, expected_length, expected_bytes)
