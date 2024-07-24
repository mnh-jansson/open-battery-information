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
        self.set_icon("icon.png")

        self.main_app = None
        self.loaded_modules = {}
        self.loaded_interfaces = {}
        self.module_names = {}
        self.interface_names = {} 

        self.setup_sidebar()
        self.setup_main_window()
        self.setup_debug_frame()

        self.default_module = DefaultModule(self.main_window)
        self.display_default_content()

        self.current_interface = None

    def set_icon(self, icon_path):
        if hasattr(sys, '_MEIPASS'):
            # When running from a PyInstaller bundle
            icon_path = os.path.join(sys._MEIPASS, icon_path)

        icon = tk.PhotoImage(file=icon_path)
        self.iconphoto(False, icon)

    def setup_sidebar(self):
        self.sidebar = tk.LabelFrame(self, text="Settings", width=200, padx=10, pady=10)
        self.sidebar.pack(fill='y', side='left')

        self.setup_module_frame()
        self.setup_interface_frame()

    def setup_module_frame(self):
        module_frame = tk.LabelFrame(self.sidebar, text="Module Selection", padx=10, pady=10)
        module_frame.pack(fill='both', pady=10)

        self.module_var = tk.StringVar()
        self.module_combobox = ttk.Combobox(module_frame, textvariable=self.module_var, width=20)
        self.module_combobox.pack(fill='both', pady=10)

        self.load_modules()
        self.module_combobox.bind("<<ComboboxSelected>>", self.display_module)

    def setup_interface_frame(self):
        interface_frame = tk.LabelFrame(self.sidebar, text="Select Interface:", padx=10, pady=10)
        interface_frame.pack(pady=10)

        self.interface_var = tk.StringVar()
        self.interface_combobox = ttk.Combobox(interface_frame, textvariable=self.interface_var, width=25)
        self.interface_combobox.pack(pady=10)

        self.load_interfaces()
        self.interface_combobox.bind("<<ComboboxSelected>>", self.display_interface_settings)

        self.interface_wireframe = tk.Frame(interface_frame, padx=10, pady=10)
        self.interface_wireframe.pack(fill='both', expand=True, pady=(20, 0))

    def setup_main_window(self):
        self.main_window = tk.Frame(self, padx=20, pady=20)
        self.main_window.pack(fill='both', expand=True, side='top')

    def setup_debug_frame(self):
        debug_frame = tk.LabelFrame(self, text="Debug Information", padx=20, pady=20)
        debug_frame.pack(fill='both', expand=False, side='top', padx=5, pady=5)

        self.debug_text = tk.Text(debug_frame, height=5, wrap='word')
        self.debug_text.pack(fill='both', expand=True)
        self.debug_text.config(state='disabled')

    def get_resource_path(self, relative_path):
        """ Get the absolute path to the resource, works for dev and for PyInstaller """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def load_modules(self):
        modules_dir = self.get_resource_path('modules')
        module_names = sorted({name for _, name, _ in pkgutil.iter_modules([modules_dir])})

        display_names = []
        for module_name in module_names:
            try:
                module = self.import_module(f"modules.{module_name}")
                display_name = module.get_display_name()
                self.module_names[display_name] = module_name
                display_names.append(display_name)
            except Exception as e:
                self.update_debug(f"Failed to load module '{module_name}': {e}")

        self.module_combobox['values'] = display_names

    def load_interfaces(self):
        interfaces_dir = self.get_resource_path('interfaces')
        interface_names = sorted({name for _, name, _ in pkgutil.iter_modules([interfaces_dir])})

        display_names = []
        for interface_name in interface_names:
            try:
                interface = self.import_module(f"interfaces.{interface_name}")
                display_name = interface.get_display_name()
                self.interface_names[display_name] = interface_name
                display_names.append(display_name)
            except Exception as e:
                self.update_debug(f"Failed to load interface '{interface_name}': {e}")

        self.interface_combobox['values'] = display_names

    def display_default_content(self):
        self.clear_main_window()
        self.default_module.pack(fill='both', expand=True)

    def display_module(self, event=None):
        display_name = self.module_var.get()
        selected_module = self.module_names.get(display_name, None)

        if selected_module:
            module_to_display = self.load_cached_module(selected_module)
            self.clear_main_window()
            self.main_app = module_to_display.ModuleApplication(self.main_window, None, self)
            self.main_app.set_interface(self.current_interface)

    def display_interface_settings(self, event=None):
        display_name = self.interface_var.get()
        selected_interface = self.interface_names.get(display_name, None)

        if selected_interface:
            interface_module = self.load_cached_interface(selected_interface)
            if self.current_interface:
                self.current_interface.pack_forget()
            self.current_interface = interface_module.Interface(self.interface_wireframe, self)
            self.current_interface.pack(fill='both', expand=True)
            if self.main_app:
                self.main_app.set_interface(self.current_interface)

    def load_cached_module(self, module_name):
        if module_name not in self.loaded_modules:
            module_to_display = self.import_module(f"modules.{module_name}")
            self.loaded_modules[module_name] = module_to_display
            self.update_debug(f"Imported module: {module_name}")
        else:
            module_to_display = self.loaded_modules[module_name]
            self.update_debug(f"Using cached module: {module_name}")
        return module_to_display

    def load_cached_interface(self, interface_name):
        if interface_name not in self.loaded_interfaces:
            interface_module = self.import_module(f"interfaces.{interface_name}")
            self.loaded_interfaces[interface_name] = interface_module
            self.update_debug(f"Imported interface: {interface_name}")
        else:
            interface_module = self.loaded_interfaces[interface_name]
            self.update_debug(f"Using cached interface: {interface_name}")
        return interface_module

    def import_module(self, module_path):
        return importlib.import_module(module_path)

    def clear_main_window(self):
        for widget in self.main_window.winfo_children():
            widget.pack_forget()

    def update_debug(self, message):
        if hasattr(self, 'debug_text'):  # Check if debug_text is initialized
            self.debug_text.config(state='normal')
            self.debug_text.insert('end', message + '\n')
            self.debug_text.see('end')
            self.debug_text.config(state='disabled')
        else:
            print("Debug:", message)  # Fallback if debug_text isn't initialized

if __name__ == "__main__":
    obi = OBI()
    obi.mainloop()
