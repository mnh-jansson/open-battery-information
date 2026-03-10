from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
import serial
import serial.tools.list_ports

INTERFACE_VERSION_CMD = [0x01, 0x00, 0x03, 0x01]
DEFAULT_BAUD_RATE = 9600


def get_display_name():
    return "Arduino OBI"


# ──────────────────────────────────────────────────────────────────────────────
# Background worker — runs a single request() on a QThread so the UI never
# freezes during serial I/O.
# ──────────────────────────────────────────────────────────────────────────────

class _SerialWorker(QObject):
    finished = Signal(object)   # response bytes, or None for fire-and-forget
    error = Signal(str)

    def __init__(self, serial_port: serial.Serial, request: list,
                 max_attempts: int, debug_cb):
        super().__init__()
        self._serial = serial_port
        self._request = request
        self._max_attempts = max_attempts
        self._debug = debug_cb

    def run(self):
        try:
            self.finished.emit(self._execute())
        except Exception as e:
            self.error.emit(str(e))

    def _execute(self):
        if not self._serial.is_open:
            raise Exception("Serial port is not open.")

        for attempt in range(1, self._max_attempts + 1):
            # Bytes [0..2] are protocol framing header; [3:] is the logical payload.
            self._debug(
                f">> {' '.join(f'{x:02X}' for x in self._request[3:])}")
            try:
                self._serial.reset_input_buffer()
                self._serial.write(bytearray(self._request))

                response = self._serial.read(self._request[2] + 2)
                self._debug(f"<< {' '.join(f'{x:02X}' for x in response[2:])}")

                if self._request[2] == 0:   # fire-and-forget command
                    return None

                if len(response) == self._request[2] + 2:
                    if all(b == 0xFF for b in response[2:]):
                        raise ValueError(
                            "Invalid response: all bytes are 0xFF")
                    return response

            except Exception as e:
                self._debug(
                    f"Attempt {attempt}/{self._max_attempts} failed: {e}")

        raise Exception(
            f"No valid response after {self._max_attempts} attempts.")


# ──────────────────────────────────────────────────────────────────────────────
# Interface widget
# ──────────────────────────────────────────────────────────────────────────────

class Interface(QWidget):
    def __init__(self, parent, obi_instance):
        super().__init__(parent)
        self.obi_instance = obi_instance
        self.serial = serial.Serial()
        self.serial.timeout = 1
        self._threads: list[QThread] = []   # keep all running threads alive
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Port row
        layout.addWidget(self._small_label("Serial Port"))
        self.port_combo = QComboBox()
        self.port_combo.addItems(self._get_ports())
        layout.addWidget(self.port_combo)

        layout.addSpacing(4)

        # Connect / Refresh buttons
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setProperty("accent", True)
        self.connect_btn.setStyle(self.connect_btn.style())   # re-polish
        self.connect_btn.clicked.connect(self._toggle_connection)
        layout.addWidget(self.connect_btn)

        refresh_btn = QPushButton("Refresh Ports")
        refresh_btn.clicked.connect(self._refresh_ports)
        layout.addWidget(refresh_btn)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #2E3340;")
        layout.addWidget(line)

        # Version
        self.version_label = QLabel("Firmware: —")
        self.version_label.setStyleSheet("color: #5A9E6F; font-size: 9pt;")
        layout.addWidget(self.version_label)

    @staticmethod
    def _small_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 8pt; color: #5A6070; font-weight: 600; "
                          "letter-spacing: 0.5px; text-transform: uppercase;")
        return lbl

    # ── helpers ───────────────────────────────────────────────────────────────

    def _get_ports(self) -> list[str]:
        return [p.device for p in serial.tools.list_ports.comports()]

    def _refresh_ports(self):
        current = self.port_combo.currentText()
        ports = self._get_ports()
        self.port_combo.clear()
        self.port_combo.addItems(ports)
        # Restore selection if port is still present
        if current in ports:
            self.port_combo.setCurrentText(current)

    def _set_controls_enabled(self, enabled: bool):
        """Lock/unlock port controls during an async operation."""
        self.port_combo.setEnabled(enabled)
        self.connect_btn.setEnabled(enabled)

    # ── connection ────────────────────────────────────────────────────────────

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

        # Validate the port still exists (user may not have refreshed)
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

    # ── async version read ────────────────────────────────────────────────────

    def _update_version_async(self):
        """Read firmware version off the main thread so the UI stays responsive."""
        self._set_controls_enabled(False)   # lock during read

        def on_done(response):
            if response:
                version = '.'.join(str(b) for b in response[2:])
                self.version_label.setText(f"Firmware: {version}")
            self._set_controls_enabled(True)

        def on_error(msg):
            self.version_label.setText("Firmware: error")
            self.obi_instance.update_debug(
                f"[WARN] Version read failed: {msg}")
            self._set_controls_enabled(True)

        self._run_async(INTERFACE_VERSION_CMD, max_attempts=5,
                        on_finished=on_done, on_error=on_error)

    # ── threading ─────────────────────────────────────────────────────────────

    def _run_async(self, request: list, max_attempts: int = 2,
                   on_finished=None, on_error=None):
        """
        Run a serial request on a QThread.
        The thread is kept in self._threads until it finishes, preventing
        premature garbage collection.
        """
        thread = QThread()
        worker = _SerialWorker(self.serial, request, max_attempts,
                               self.obi_instance.update_debug)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)

        if on_finished:
            worker.finished.connect(on_finished)
        if on_error:
            worker.error.connect(on_error)

        # Clean up when done
        def _cleanup():
            if thread in self._threads:
                self._threads.remove(thread)
            worker.deleteLater()

        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(_cleanup)

        self._threads.append(thread)
        thread.start()

    # ── public synchronous API ────────────────────────────────────────────────

    def request(self, request: list, max_attempts: int = 2):
        """
        Synchronous serial request — called by module code.
        Protocol framing: bytes [0..2] are header/length; [3:] is the logged payload.
        For non-blocking module calls, expose request_async() in a future iteration.
        """
        if not self.serial.is_open:
            raise Exception("Serial port is not open.")

        for attempt in range(1, max_attempts + 1):
            self.obi_instance.update_debug(
                f">> {' '.join(f'{x:02X}' for x in request[3:])}"
            )
            try:
                self.serial.reset_input_buffer()
                self.serial.write(bytearray(request))

                response = self.serial.read(request[2] + 2)
                self.obi_instance.update_debug(
                    f"<< {' '.join(f'{x:02X}' for x in response[2:])}"
                )

                if request[2] == 0:
                    return None

                if len(response) == request[2] + 2:
                    if all(b == 0xFF for b in response[2:]):
                        raise ValueError(
                            "Invalid response: all bytes are 0xFF")
                    return response

            except Exception as e:
                self.obi_instance.update_debug(
                    f"Attempt {attempt}/{max_attempts} failed: {e}"
                )

        raise Exception(f"No valid response after {max_attempts} attempts.")
