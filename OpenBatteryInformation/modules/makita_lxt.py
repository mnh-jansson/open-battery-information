from tkinter import ttk
from tkinter import messagebox
import tkinter as tk

def get_display_name():
    return "Makita LXT"

READ_STATIC_REQUEST = [0x01, 2, 16, 0xcc, 0xdc, 0x0c]
READ_DATA_REQUEST = [0x01, 4, 29, 0xcc, 0xd7, 0x00, 0x00, 0xff]
ENTER_TESTMODE = [0x01, 3, 0, 0x33, 0xd9, 0x96, 0xa5]
ALL_LEDS_ON_REQUEST = [0x01, 2, 0, 0x33, 0xda, 0x31]
ALL_LEDS_OFF_REQUEST = [0x01, 2, 0, 0x33, 0xda, 0x34]
RESET_ERRORS_REQUEST = [0x01, 2, 0, 0x33, 0xda, 0x04]
RESET_MESSAGE_REQUESTS = [
    [0x01, 3, 0, 0x33, 0xd9, 0x96, 0xa5],
    [0x01, 2, 0, 0xcc, 0xf0, 0x00],
    [0x01, 34, 0, 0x33, 0x33, 0x0f, 0x00, 0xF1, 0x26, 0xBD, 0x13, 0x14, 0x58, 0x0, 0x0, 0x94, 0x94, 0x40, 0x21, 0xD0, 0x80, 0x2, 0x4E, 0x23, 0xD0, 0x8E, 0x45, 0x60, 0x1A, 0x0, 0x3, 0x2, 0x2, 0x0E, 0x20, 0x0, 0x30, 0x1, 0x83],
    [0x01, 2, 0, 0x33, 0x55, 0xa5]
]

class ModuleApplication(tk.Frame):
    def __init__(self, parent, interface_module=None, obi_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.interface = None
        self.interface_module = interface_module
        self.obi_instance = obi_instance
        self.create_widgets()

    def set_interface(self, interface_instance):
        self.interface = interface_instance

    def create_widgets(self):
        label = tk.Label(self, text="Makita", font=('Helvetica', 16))
        label.pack(pady=20)

        columns_frame = tk.Frame(self)
        columns_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns_frame.grid_columnconfigure(0, weight=1)
        column_frame = tk.LabelFrame(columns_frame, text="Read data")
        column_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        # Store buttons in a list for easy management
        self.buttons = []

        button1 = tk.Button(column_frame, text="Read static data", command=self.on_read_static_click)
        button1.pack(pady=10)
        self.buttons.append(button1)

        button2 = tk.Button(column_frame, text="Read battery data", command=self.on_read_data_click, state=tk.DISABLED)
        button2.pack(pady=10)
        self.buttons.append(button2)

        columns_frame.grid_columnconfigure(1, weight=1)
        column_frame = tk.LabelFrame(columns_frame, text="Function test")
        column_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

        button3 = tk.Button(column_frame, text="All leds ON", command=self.on_all_leds_on_click, state=tk.DISABLED)
        button3.pack(pady=10)
        self.buttons.append(button3)

        button4 = tk.Button(column_frame, text="All leds OFF", command=self.on_all_leds_off_click, state=tk.DISABLED)
        button4.pack(pady=10)
        self.buttons.append(button4)

        columns_frame.grid_columnconfigure(2, weight=1)
        column_frame = tk.LabelFrame(columns_frame, text="Reset battery")
        column_frame.grid(row=0, column=2, sticky='nsew', padx=10, pady=10)

        button5 = tk.Button(column_frame, text="Reset errors", command=self.on_reset_errors_click, state=tk.DISABLED)
        button5.pack(pady=10)
        self.buttons.append(button5)

        button6 = tk.Button(column_frame, text="Reset battery message", command=self.on_reset_message_click, state=tk.DISABLED)
        button6.pack(pady=10)
        self.buttons.append(button6)

        self.tree = ttk.Treeview(self, columns=("Value"))
        self.tree.heading("#0", text="Parameter")
        self.tree.heading("Value", text="Value")
        self.tree.pack(pady=20, padx=20, fill='both', expand=True)
        self.tree.tag_configure('evenrow', background='lightgrey')
        self.tree.tag_configure('oddrow', background='white')

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

    def on_read_static_click(self):
        if self.interface:
                        
            try:
                response = self.interface.request(READ_STATIC_REQUEST)
                model = response[2:9].decode('utf-8')
            except Exception as e:
                tk.messagebox.showerror("Error", f"{e}")
                return

            data = {"Model": model}
            self.insert_battery_data(data)
            self.enable_all_buttons()

    def on_read_data_click(self):
        if self.interface:
            try:
                response = self.interface.request(READ_DATA_REQUEST)
            except Exception as e:
                tk.messagebox.showerror("Error", f"{e}")
                return   

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

    def on_all_leds_on_click(self):
        if self.interface:
            self.interface.request(ENTER_TESTMODE)
            self.interface.request(ALL_LEDS_ON_REQUEST)

    def on_all_leds_off_click(self):
        if self.interface:
            self.interface.request(ENTER_TESTMODE)
            self.interface.request(ALL_LEDS_OFF_REQUEST)

    def on_reset_errors_click(self):
        if self.interface:
            self.interface.request(ENTER_TESTMODE)
            self.interface.request(RESET_ERRORS_REQUEST)

    def on_reset_message_click(self):
        if self.interface:
            for request in RESET_MESSAGE_REQUESTS:
                self.interface.request(request)

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
