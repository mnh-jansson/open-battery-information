from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
import time

def get_display_name():
    return "Makita LXT"

# Command Definitions
MODEL_CMD           = [0x01, 0x02, 0x10, 0xCC, 0xDC, 0x0C]
READ_DATA_REQUEST   = [0x01, 0x04, 0x1D, 0xCC, 0xD7, 0x00, 0x00, 0xFF]
TESTMODE_CMD        = [0x01, 0x03, 0x09, 0x33, 0xD9, 0x96, 0xA5]
LEDS_ON_CMD         = [0x01, 0x02, 0x09, 0x33, 0xDA, 0x31]
LEDS_OFF_CMD        = [0x01, 0x02, 0x09, 0x33, 0xDA, 0x34]
RESET_ERROR_CMD     = [0x01, 0x02, 0x09, 0x33, 0xDA, 0x04]
ROMID_CHARGER_CMD   = [0x01, 0x02, 0x28, 0x33, 0xF0, 0x00]
CHARGER_CMD         = [0x01, 0x02, 0x20, 0xCC, 0xF0, 0x00]
READ_MSG_CMD        = [0x01, 0x02, 0x28, 0x33, 0xAA, 0x00]
CLEAR_CMD           = [0x01, 0x02, 0x00, 0xCC, 0xF0, 0x00]
STORE_CMD           = [0x01, 0x02, 0x00, 0x33, 0x55, 0xA5]
CLEAN_FRAME_CMD     = [0x01, 0x22, 0x00, 0x33, 0x33, 0x0F, 0x00, 0xF1, 0x26, 0xBD, 0x13, 0x14, 0x58, 0x00, 0x00, 0x94, 0x94, 0x40, 0x21, 0xD0, 0x80, 0x02, 0x4E, 0x23, 0xD0, 0x8E, 0x45, 0x60, 0x1A, 0x00, 0x03, 0x02, 0x02, 0x0E, 0x20, 0x00, 0x30, 0x01, 0x83]


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

initial_data = {
    "Model": "",
    "Charge count*": "",
    "State": "",
    "Status code": "",
    "Pack Voltage": "",
    "Cell 1 Voltage": "",
    "Cell 2 Voltage": "",
    "Cell 3 Voltage": "",
    "Cell 4 Voltage": "",
    "Cell 5 Voltage": "",
    "Cell Voltage Difference": "",
    "Temperature Sensor 1": "",
    "Temperature Sensor 2": "",
    "ROM ID": "",
    "Manufacturing date": "",
    "Battery message": "",
    "Capacity": "",
    "Battery type": "",
}

class ModuleApplication(tk.Frame):
    def __init__(self, parent, interface_module=None, obi_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.interface = None
        self.interface_module = interface_module
        self.obi_instance = obi_instance
        self.command_version = None
        self.battery_present = False
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

        button6 = tk.Button(column_frame, text="Reset battery message", command=self.on_reset_message_click, state=tk.DISABLED)
        button6.pack(pady=10)
        button6.config(width=20)
        self.buttons.append(button6)

        tree_frame = tk.Frame(self)
        tree_frame.pack(pady=20, padx=20, fill='both', expand=True)

        tree_scroll_y = tk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            tree_frame, 
            columns=("Value"), 
            yscrollcommand=tree_scroll_y.set,
        )
        
        tree_scroll_y.config(command=self.tree.yview)

        self.tree.heading("#0", text="Parameter")
        self.tree.heading("Value", text="Value")

        self.tree.tag_configure('evenrow', background='lightgrey')
        self.tree.tag_configure('oddrow', background='white')

        self.tree.pack(pady=1, padx=1, fill='both', expand=True)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=1, padx=1, anchor='center')

        copy_button = tk.Button(button_frame, text="Copy", command=self.copy_to_clipboard)
        copy_button.pack(side="left", padx=5)

        clear_button = tk.Button(button_frame, text="Clear", command=self.clear_data)
        clear_button.pack(side="left", padx=5)

        button_frame.pack(expand=True)

        self.pack(fill='both', expand=True)

        self.insert_battery_data(initial_data)

    def enable_all_buttons(self):
        """Enable all buttons."""
        for button in self.buttons:
            button.config(state=tk.NORMAL)
    
    def get_model(self):
        try:
            response = self.interface.request(MODEL_CMD)
            model = response[2:9].decode('utf-8')
            self.enable_all_buttons()
            self.command_version = ""
            return model
        except Exception as e:
            raise e

    def get_f0513_model(self):
        try:
            # This is currently handled in the interface as there were timing issues. TODO
            #self.interface.request(F0513_TESTMODE_CMD)
            response = self.interface.request(F0513_MODEL_CMD)
            self.interface.request(CLEAR_CMD)
            self.command_version = "F0513"
            messagebox.showwarning("Limited", "This model only supports diagnostics")
            self.buttons[1].config(state=tk.NORMAL)
            return (f"BL{response[2]:X}{response[3]:X}")
        except Exception as e:
            raise e
    def nibble_swap(self, byte):
        upper_nibble = (byte & 0xF0) >> 4  # Extract the upper nibble and shift right by 4 bits
        lower_nibble = (byte & 0x0F) << 4  # Extract the lower nibble and shift left by 4 bits
        swapped_byte = upper_nibble | lower_nibble  # Combine the nibbles
        return swapped_byte

    def on_read_static_click(self):
        commands = [self.get_model, self.get_f0513_model]

        if not self.interface:
            tk.messagebox.showerror("Error", "No interface specified.")
            return
        try:
            response = self.interface.request(READ_MSG_CMD)
            rom_id = ' '.join(f'{byte:02X}' for byte in response[2:10])
            raw_msg = ' '.join(f'{byte:02X}' for byte in response[10:42])
            swapped_bytes = bytearray([self.nibble_swap(response[37]), self.nibble_swap(response[36])])[::-1]
            charge_count = int.from_bytes(swapped_bytes, byteorder='big')
            charge_count = charge_count & 0x0FFF
            lock_nibble = response[30] & 0x0F
            error_byte = response[29]
            if lock_nibble > 0:
                lock_status = "LOCKED"
            else:
                lock_status = "UNLOCKED"
            data = {"ROM ID": rom_id,
                    "Battery message": raw_msg,
                    "Charge count*": charge_count,
                    "State": lock_status,
                    "Status code": f'{error_byte:02X}',
                    "Manufacturing date": f'{response[4]:02}/{response[3]:02}/20{response[2]:02}',
                    "Capacity": f'{self.nibble_swap(response[26])/10}Ah',
                    "Battery type": self.nibble_swap(response[21]),
            }
            self.insert_battery_data(data)
            self.battery_present = True
        except Exception as e:
            tk.messagebox.showerror("Error", f"{e}")
            return

        for command in commands:

            try:
                model = command()

                data = {"Model": model}
                self.insert_battery_data(data)
                return

            except Exception as e:
                last_exception = e

        tk.messagebox.showerror("Error", "Battery is present but not supported.")

    def on_read_data_click(self):
        if not self.interface:
            tk.messagebox.showerror("Error", "No interface specified.")
            return

        try:
            if self.command_version == 'F0513':
                self.interface.request(CLEAR_CMD)
                self.interface.request(CLEAR_CMD)
                cell1 = self.interface.request(F0513_VCELL_1_CMD)
                cell2 = self.interface.request(F0513_VCELL_2_CMD)
                cell3 = self.interface.request(F0513_VCELL_3_CMD)
                cell4 = self.interface.request(F0513_VCELL_4_CMD)
                cell5 = self.interface.request(F0513_VCELL_5_CMD)
                temp = self.interface.request(F0513_TEMP_CMD)
                v_cell1 = int.from_bytes(cell1[2:4], byteorder='little') / 1000
                v_cell2 = int.from_bytes(cell2[2:4], byteorder='little') / 1000
                v_cell3 = int.from_bytes(cell3[2:4], byteorder='little') / 1000
                v_cell4 = int.from_bytes(cell4[2:4], byteorder='little') / 1000
                v_cell5 = int.from_bytes(cell5[2:4], byteorder='little') / 1000
                voltages = [v_cell1,v_cell2,v_cell3,v_cell4,v_cell5]
                v_pack = sum(voltages)
                v_diff = round(max(voltages) - min(voltages), 2)
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
                voltages = [v_cell1,v_cell2,v_cell3,v_cell4,v_cell5]
                v_diff = round(max(voltages) - min(voltages), 2)
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
            # TODO: Replace clean frame with the frame from the battery.
            # 1. Read frame
            # 2. set nibble 0
            # 3. write as usual 
            tk.messagebox.showerror("Error", "This feature is currently under development.")
            return
        
            self.interface.request(TESTMODE_CMD)
            self.interface.request(CHARGER_CMD)
            self.interface.request(CLEAN_FRAME_CMD)
            self.interface.request(STORE_CMD)

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

    def copy_to_clipboard(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "No rows selected to copy!")
            return

        rows = []
        for item in selected_items:
            values = self.tree.item(item, 'values')
            row_text = '\t'.join(values)
            rows.append(row_text)

        self.parent.clipboard_clear()
        self.parent.clipboard_append('\n'.join(rows))
        messagebox.showinfo("Copied", "Selected rows have been copied to the clipboard.")

    def clear_data(self):
        self.insert_battery_data(initial_data)