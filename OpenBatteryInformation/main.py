import os
import sys
import tkinter as tk
from tkinter import ttk
import importlib.util
import pkgutil
from components.default_module import DefaultModule

class OBI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OBI-1")
        self.geometry("1270x720")

        self.main_app = None
        self.loaded_modules = {}
        self.loaded_interfaces = {}

        self.sidebar = tk.LabelFrame(self, text="Settings", width=200, padx=10, pady=10)
        self.sidebar.pack(fill='y', side='left')

        module_frame = tk.LabelFrame(self.sidebar, text="Module Selection", padx=10, pady=10)
        module_frame.pack(fill='both', pady=10)

        self.module_var = tk.StringVar()
        self.module_combobox = ttk.Combobox(module_frame, textvariable=self.module_var, width=20)
        self.module_combobox.pack(fill='both', pady=10)

        self.load_modules()

        interface_frame = tk.LabelFrame(self.sidebar, text="Select Interface:", padx=10, pady=10)
        interface_frame.pack(pady=10)

        self.interface_var = tk.StringVar()
        self.interface_combobox = ttk.Combobox(interface_frame, textvariable=self.interface_var, width=25)
        self.interface_combobox.pack(pady=10)

        self.load_interfaces()

        self.interface_wireframe = tk.Frame(interface_frame, padx=10, pady=10)
        self.interface_wireframe.pack(fill='both', expand=True, pady=(20, 0))

        self.main_window = tk.Frame(self, padx=20, pady=20)
        self.main_window.pack(fill='both', expand=True, side='top')

        debug_frame = tk.LabelFrame(self, text="Debug Information", padx=20, pady=20)
        debug_frame.pack(fill='both', expand=False, side='top', padx=5, pady=5)

        self.debug_text = tk.Text(debug_frame, height=5, wrap='word')
        self.debug_text.pack(fill='both', expand=True)
        self.debug_text.config(state='disabled')

        self.default_module = DefaultModule(self.main_window)
        self.display_default_content()

        self.module_combobox.bind("<<ComboboxSelected>>", self.display_module)
        self.interface_combobox.bind("<<ComboboxSelected>>", self.display_interface_settings)

        self.current_interface = None

    def get_resource_path(self, relative_path):
        """ Get the absolute path to the resource, works for dev and for PyInstaller """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def load_modules(self):
        modules_dir = self.get_resource_path('modules')
        module_names = sorted({name for _, name, _ in pkgutil.iter_modules([modules_dir])})
        self.module_combobox['values'] = list(module_names)

    def load_interfaces(self):
        interfaces_dir = self.get_resource_path('interfaces')
        interface_names = sorted({name for _, name, _ in pkgutil.iter_modules([interfaces_dir])})
        self.interface_combobox['values'] = list(interface_names)

    def display_default_content(self):
        self.clear_main_window()
        self.default_module.pack(fill='both', expand=True)

    def display_module(self, event=None):
        selected_module = self.module_var.get()

        if selected_module:
            try:
                if selected_module not in self.loaded_modules:
                    module_to_display = importlib.import_module(f"modules.{selected_module}")
                    self.loaded_modules[selected_module] = module_to_display
                    self.update_debug(f"Imported module: {selected_module}")
                else:
                    module_to_display = self.loaded_modules[selected_module]
                    self.update_debug(f"Using cached module: {selected_module}")

                self.clear_main_window()

                self.main_app = module_to_display.ModuleApplication(self.main_window, None, self)
                self.main_app.set_interface(self.current_interface)

            except ImportError as e:
                self.update_debug(f"Error loading module: {e}")

    def display_interface_settings(self, event=None):
        selected_interface = self.interface_var.get()
        if selected_interface:
            try:
                if selected_interface not in self.loaded_interfaces:
                    interface_module = importlib.import_module(f"interfaces.{selected_interface}")
                    self.loaded_interfaces[selected_interface] = interface_module
                    self.update_debug(f"Imported interface: {selected_interface}")
                else:
                    interface_module = self.loaded_interfaces[selected_interface]
                    self.update_debug(f"Using cached interface: {selected_interface}")

                if self.current_interface:
                    self.current_interface.pack_forget()

                self.current_interface = interface_module.Interface(self.interface_wireframe, self)
                self.current_interface.pack(fill='both', expand=True)

                if self.main_app and hasattr(self.main_app, 'set_interface') and callable(self.main_app.set_interface):
                    self.main_app.set_interface(self.current_interface)

            except ImportError as e:
                self.update_debug(f"Error loading interface: {e}")

    def clear_main_window(self):
        for widget in self.main_window.winfo_children():
            widget.pack_forget()

    def update_debug(self, message):
        self.debug_text.config(state='normal')

        self.debug_text.insert('end', message + '\n')

        self.debug_text.see('end')

        self.debug_text.config(state='disabled')

if __name__ == "__main__":
    obi = OBI()
    obi.mainloop()
