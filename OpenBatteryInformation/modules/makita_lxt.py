from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
import time

def get_display_name():
    return "Makita LXT"

# Command Definitions
MODEL_CMD           = [0x01, 0x02, 0x10, 0xCC, 0xDC, 0x0C]
READ_DATA_REQUEST   = [0x01, 0x04, 0x1D, 0xCC, 0xD7, 0x00, 0x00, 0xFF]
TESTMODE_CMD        = [0x01, 0x03, 0x00, 0x33, 0xD9, 0x96, 0xA5]
LEDS_ON_CMD         = [0x01, 0x02, 0x00, 0x33, 0xDA, 0x31]
LEDS_OFF_CMD        = [0x01, 0x02, 0x00, 0x33, 0xDA, 0x34]
RESET_ERROR_CMD     = [0x01, 0x02, 0x00, 0x33, 0xDA, 0x04]

RESET_ERROR_CMD     = [0x01, 0x02, 0x00, 0x33, 0xDA, 0x04]

RESET_MESSAGE_REQUESTS = [
    [0x01, 0x03, 0x00, 0x33, 0xD9, 0x96, 0xA5],
    [0x01, 0x02, 0x00, 0xCC, 0xF0, 0x00],
    [0x01, 0x22, 0x00, 0x33, 0x33, 0x0F, 0x00, 0xF1, 0x26, 0xBD, 0x13, 0x14, 0x58, 0x00, 0x00, 0x94, 0x94, 0x40, 0x21, 0xD0, 0x80, 0x02, 0x4E, 0x23, 0xD0, 0x8E, 0x45, 0x60, 0x1A, 0x00, 0x03, 0x02, 0x02, 0x0E, 0x20, 0x00, 0x30, 0x01, 0x83],
    [0x01, 0x02, 0x00, 0x33, 0x55, 0xA5]
]

# Commands specific to the F0513 version
F0513_VCELL_1_CMD   = [0x01, 0x01, 0x02, 0xCC, 0x31]
F0513_VCELL_2_CMD   = [0x01, 0x01, 0x02, 0xCC, 0x32]
F0513_VCELL_3_CMD   = [0x01, 0x01, 0x02, 0xCC, 0x33]
F0513_VCELL_4_CMD   = [0x01, 0x01, 0x02, 0xCC, 0x34]
F0513_VCELL_5_CMD   = [0x01, 0x01, 0x02, 0xCC, 0x35]
F0513_TEMP_CMD      = [0x01, 0x01, 0x02, 0xCC, 0x52]
F0513_MODEL_CMD     = [0x01, 0x00, 0x02, 0x31]
F0513_VERSION_CMD   = [0x01, 0x00, 0x02, 0x32]
F0513_TESTMODE_CMD  = [0x01, 0x01, 0x00, 0xCC, 0x99]

class ModuleApplication(tk.Frame):
    def __init__(self, parent, interface_module=None, obi_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.interface = None
        self.interface_module = interface_module
        self.obi_instance = obi_instance
        self.command_version = None  # Track the command version
        self.create_widgets()

    def set_interface(self, interface_instance):
        self.interface = interface_instance

    def create_widgets(self):
        label = tk.Label(self, text=get_display_name(), font=('Helvetica', 16))
        label.pack(pady=20)

        columns_frame = tk.Frame(self)
        columns_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns_frame.grid_columnconfigure(0, weight=1)
        column_frame = tk.LabelFrame(columns_frame, text="Read data")
        column_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        # Store buttons in a list for easy management
        self.buttons = []

        button1 = tk.Button(column_frame, text="Read battery model", command=self.on_read_static_click)
        button1.pack(pady=10)
        button1.config(width=20)
        self.buttons.append(button1)

        button2 = tk.Button(column_frame, text="Read battery data", command=self.on_read_data_click, state=tk.DISABLED)
        button2.pack(pady=10)
        button2.config(width=20)
        self.buttons.append(button2)

        columns_frame.grid_columnconfigure(1, weight=1)
        column_frame = tk.LabelFrame(columns_frame, text="Function test")
        column_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

        button3 = tk.Button(column_frame, text="LED test ON", command=self.on_all_leds_on_click, state=tk.DISABLED)
        button3.pack(pady=10)
        button3.config(width=20)
        self.buttons.append(button3)

        button4 = tk.Button(column_frame, text="LED test OFF", command=self.on_all_leds_off_click, state=tk.DISABLED)
        button4.pack(pady=10)
        button4.config(width=20)
        self.buttons.append(button4)

        columns_frame.grid_columnconfigure(2, weight=1)
        column_frame = tk.LabelFrame(columns_frame, text="Reset battery")
        column_frame.grid(row=0, column=2, sticky='nsew', padx=10, pady=10)

        button5 = tk.Button(column_frame, text="Clear errors", command=self.on_reset_errors_click, state=tk.DISABLED)
        button5.pack(pady=10)
        button5.config(width=20)
        self.buttons.append(button5)

        button6 = tk.Button(column_frame, text="Clear battery message", command=self.on_reset_message_click, state=tk.DISABLED)
        button6.pack(pady=10)
        button6.config(width=20)
        self.buttons.append(button6)

        self.tree = ttk.Treeview(self, columns=("Value"))
        self.tree.heading("#0", text="Parameter")
        self.tree.heading("Value", text="Value")
        self.tree.pack(pady=20, padx=20, fill='both', expand=True)
        self.tree.tag_configure('evenrow', background='lightgrey')
        self.tree.tag_configure('oddrow', background='white')
        self.enable_all_buttons()

        self.pack(fill='both', expand=True)

        initial_data = {
            "Model": "",
            "Pack Voltage": "",
            "Cell 1 Voltage": "",
            "Cell 2 Voltage": "",
            "Cell 3 Voltage": "",
            "Cell 4 Voltage": "",
            "Cell 5 Voltage": "",
            "Cell Voltage Difference": "",
            "Temperature Sensor 1": "",
            "Temperature Sensor 2": ""
        }

        self.insert_battery_data(initial_data)

    def enable_all_buttons(self):
        """Enable all buttons."""
        for button in self.buttons:
            button.config(state=tk.NORMAL)
    
    def get_model(self):
        print("trying default")
        try:
            response = self.interface.request(MODEL_CMD)
            model = response[2:9].decode('utf-8')
            return model
        except Exception as e:
            raise e

    def get_f0513_model(self):
        print("trying f0513")
        try:
            self.interface.request(F0513_TESTMODE_CMD)
            response = self.interface.request(F0513_MODEL_CMD)
            self.command_version = "F0513"
            return (f"BL{response[2]:X}{response[3]:X}")
        except Exception as e:
            raise e


    def on_read_static_click(self):
        """Read static data and determine command version by handling exceptions."""

        commands = [self.get_model, self.get_f0513_model]

        if not self.interface:
            tk.messagebox.showerror("Error", "No interface specified.")
            return

        last_exception = None  # Variable to store the last exception encountered

        for command in commands:

            try:
                model = command()

                data = {"Model": model}
                self.insert_battery_data(data)
                self.enable_all_buttons()
                return

            except Exception as e:
                last_exception = e

        tk.messagebox.showerror("Error", f"{last_exception}")

    def on_read_data_click(self):
        """Read dynamic battery data based on command version."""
        if not self.interface:
            tk.messagebox.showerror("Error", "No interface specified.")
            return

        try:
            if self.command_version == 'F0513':
                cell1 = self.interface.request(F0513_VCELL_1_CMD)  # Example F0513 specific command
                cell2 = self.interface.request(F0513_VCELL_2_CMD)  # Example F0513 specific command
                cell3 = self.interface.request(F0513_VCELL_3_CMD)  # Example F0513 specific command
                cell4 = self.interface.request(F0513_VCELL_4_CMD)  # Example F0513 specific command
                cell5 = self.interface.request(F0513_VCELL_5_CMD)  # Example F0513 specific command
                temp = self.interface.request(F0513_TEMP_CMD)  # Example F0513 specific command
                v_cell1 = int.from_bytes(cell1[2:4], byteorder='little') / 1000
                v_cell2 = int.from_bytes(cell2[2:4], byteorder='little') / 1000
                v_cell3 = int.from_bytes(cell3[2:4], byteorder='little') / 1000
                v_cell4 = int.from_bytes(cell4[2:4], byteorder='little') / 1000
                v_cell5 = int.from_bytes(cell5[2:4], byteorder='little') / 1000
                voltages = [v_cell1,v_cell2,v_cell3,v_cell4,v_cell5]
                v_pack = sum(voltages)
                v_diff = max(voltages) - min(voltages)
                t_cell = int.from_bytes(temp[2:4], byteorder='little') / 100
                t_mosfet = ""
            else:
                response = self.interface.request(READ_DATA_REQUEST)
                v_pack = int.from_bytes(response[2:4], byteorder='little') / 1000
                v_cell1 = int.from_bytes(response[4:6], byteorder='little') / 1000
                v_cell2 = int.from_bytes(response[6:8], byteorder='little') / 1000
                v_cell3 = int.from_bytes(response[8:10], byteorder='little') / 1000
                v_cell4 = int.from_bytes(response[10:12], byteorder='little') / 1000
                v_cell5 = int.from_bytes(response[12:14], byteorder='little') / 1000
                v_diff = int.from_bytes(response[14:16], byteorder='little') / 100000
                t_cell = int.from_bytes(response[16:18], byteorder='little') / 100
                t_mosfet = int.from_bytes(response[18:20], byteorder='little') / 100

            battery_data = {
                "Pack Voltage": v_pack,
                "Cell 1 Voltage": v_cell1,
                "Cell 2 Voltage": v_cell2,
                "Cell 3 Voltage": v_cell3,
                "Cell 4 Voltage": v_cell4,
                "Cell 5 Voltage": v_cell5,
                "Cell Voltage Difference": v_diff,
                "Temperature Sensor 1": t_cell,
                "Temperature Sensor 2": t_mosfet
            }

            self.insert_battery_data(battery_data)

        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to read battery data: {e}")

    def on_all_leds_on_click(self):
        if not self.interface:
            tk.messagebox.showerror("Error", "No interface specified.")
            return

        try:
            self.interface.request(TESTMODE_CMD)
            self.interface.request(LEDS_ON_CMD)

        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to turn LEDs on: {e}")

    def on_all_leds_off_click(self):
        if not self.interface:
            tk.messagebox.showerror("Error", "No interface specified.")
            return

        try:
            if self.command_version == 'F0513':
                self.interface.request(F0513_TESTMODE_CMD)
            else:
                self.interface.request(TESTMODE_CMD)

            self.interface.request(LEDS_OFF_CMD)

        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to turn LEDs off: {e}")

    def on_reset_errors_click(self):
        if not self.interface:
            tk.messagebox.showerror("Error", "No interface specified.")
            return

        try:
            self.interface.request(TESTMODE_CMD)
            self.interface.request(RESET_ERROR_CMD)

        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to reset errors: {e}")

    def on_reset_message_click(self):
        if not self.interface:
            tk.messagebox.showerror("Error", "No interface specified.")
            return

        try:
            for request in RESET_MESSAGE_REQUESTS:
                self.interface.request(request)

        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to reset message: {e}")

    def insert_battery_data(self, data):
        for idx, (parameter, value) in enumerate(data.items()):
            item_id = None
            for item in self.tree.get_children():
                if self.tree.item(item, "text") == parameter:
                    item_id = item
                    break

            if item_id:
                self.tree.item(item_id, values=(value,))
            else:
                if idx % 2 == 0:
                    self.tree.insert("", "end", text=parameter, values=(value,), tags=('evenrow',))
                else:
                    self.tree.insert("", "end", text=parameter, values=(value,), tags=('oddrow',))
