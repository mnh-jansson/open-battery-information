import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports

@staticmethod
def get_display_name():
    return "Arduino OBI"

class Interface(tk.Frame):
    def __init__(self, parent, obi_instance):
        super().__init__(parent)
        self.parent = parent
        self.obi_instance = obi_instance
        self.serial = serial.Serial()
        self.serial.timeout = 1
        self.create_widgets()

    def create_widgets(self):
        serial_label = tk.Label(self, text="Serial Port:")
        serial_label.pack(pady=5)

        ports = self.get_available_serial_ports()

        self.conf_port = ttk.Combobox(self, values=ports, state="readonly")
        self.conf_port.pack(pady=5)

        self.connect_button = tk.Button(self, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(pady=10)
        self.connect_button.config(width=20)


        self.refresh_button = tk.Button(self, text="Refresh list", command=self.refresh_serial_list)
        self.refresh_button.pack(pady=10)
        self.refresh_button.config(width=20)

    def refresh_serial_list(self):
        ports = self.get_available_serial_ports()
        self.conf_port["values"] = ports


    def get_available_serial_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports

    def toggle_connection(self):
        if self.serial.is_open:
            self.close_serial_port()
        else:
            self.open_serial_port()

    def open_serial_port(self):
        selected_port = self.conf_port.get()
        if selected_port:
            self.serial.port = selected_port
            try:
                self.serial.open()
                self.obi_instance.update_debug(f"Opened serial port: {selected_port}")
                self.connect_button.config(text="Disconnect", command=self.close_serial_port)
            except Exception as e:
                self.obi_instance.update_debug(f"Error opening serial port {selected_port}: {e}")

    def close_serial_port(self):
        if self.serial.is_open:
            self.serial.close()
            self.obi_instance.update_debug("Closed serial port")
            self.connect_button.config(text="Connect", command=self.open_serial_port)

    def request(self, request, max_attempts=2):
        if not self.serial.is_open:
            raise Exception(f"Serial port is not open.")
        self.obi_instance.update_debug(f">> {' '.join(f'{x:02X}' for x in request[3:])}")

        for attempt in range(1, max_attempts + 1):
            try:
                self.serial.reset_input_buffer()
                self.serial.write(request)

                response = self.serial.read(request[2] + 2)
                #print(response)
                self.obi_instance.update_debug(f"<< {' '.join(f'{x:02X}' for x in response[0:])}")
                if request[2] == 0:
                    return

                if len(response) == request[2] + 2:
                    
                    if all(byte == 0xff for byte in response[2:]):
                        raise ValueError("Invalid response: all bytes are 0xFF")
                    
                    return response

            except Exception as e:
                self.obi_instance.update_debug(f"Attempt {attempt}/{max_attempts} failed: {e}")
        raise Exception(f"Failed to get a valid response after {max_attempts} attempts.")

