import tkinter as tk
import importlib.util
import pkgutil
from components.default_module import DefaultModule

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OBI-1")
        self.geometry("1270x720")  # Set window size

        # Sidebar with module and interface selectors
        self.sidebar = tk.LabelFrame(self, text="Settings", width=200, padx=10, pady=10)
        self.sidebar.pack(fill='y', side='left')

        # Module selection
        module_frame = tk.LabelFrame(self.sidebar, text="Module Selection", padx=10, pady=10)
        module_frame.pack(pady=10)

        self.module_var = tk.StringVar()
        self.module_dropdown = tk.OptionMenu(module_frame, self.module_var, ())
        self.module_dropdown.config(width=20)
        self.module_dropdown.pack(pady=10)

        self.load_modules()

        # Interface selection
        interface_frame = tk.LabelFrame(self.sidebar, text="Select Interface:", padx=10, pady=10)
        interface_frame.pack(pady=10)

        self.interface_var = tk.StringVar()
        self.interface_dropdown = tk.OptionMenu(interface_frame, self.interface_var, ())
        self.interface_dropdown.config(width=20)
        self.interface_dropdown.pack(pady=10)

        self.load_interfaces()

        # Wireframe for interface settings
        self.interface_wireframe = tk.Frame(interface_frame, padx=10, pady=10)
        self.interface_wireframe.pack(fill='both', expand=True, pady=(20, 0))

        # Main window area for displaying selected modules or default content
        self.main_window = tk.Frame(self, padx=20, pady=20)
        self.main_window.pack(fill='both', expand=True, side='right')

        # Create an instance of DefaultModule (default content)
        self.default_module = DefaultModule(self.main_window)
        self.display_default_content()

        self.module_var.trace('w', self.display_module)
        self.interface_var.trace('w', self.display_interface_settings)

        # Initialize a single interface instance
        self.current_interface = None

    def load_modules(self):
        modules_dir = 'modules'
        module_names = [name for _, name, _ in pkgutil.iter_modules([modules_dir])]

        for module_name in module_names:
            module = importlib.import_module(f'{modules_dir}.{module_name}')

            setattr(self, module_name, module)
            self.module_dropdown['menu'].add_command(label=module_name, command=tk._setit(self.module_var, module_name))

    def load_interfaces(self):
        interfaces_dir = 'interfaces'
        interface_names = [name for _, name, _ in pkgutil.iter_modules([interfaces_dir])]

        for interface_name in interface_names:
            interface = importlib.import_module(f'{interfaces_dir}.{interface_name}')

            setattr(self, interface_name, interface)
            self.interface_dropdown['menu'].add_command(label=interface_name, command=tk._setit(self.interface_var, interface_name))

    def display_default_content(self):
        # Display the default module content (DefaultModule)
        self.clear_main_window()
        self.default_module.pack(fill='both', expand=True)

    def display_module(self, *args):
        selected_module = self.module_var.get()
        selected_interface = self.interface_var.get()
        
        if selected_module and selected_interface:
            module_to_display = getattr(self, selected_module, None)
            interface_module = getattr(self, selected_interface, None)
            
            if module_to_display and interface_module:
                self.clear_main_window()
                # Instantiate the ModuleApplication class from the selected module
                main_app = module_to_display.ModuleApplication(self.main_window, interface_module)
                # Pass the interface instance to ModuleApplication
                main_app.set_interface(self.current_interface)

    def display_interface_settings(self, *args):
        selected_interface = self.interface_var.get()

        if selected_interface:
            interface_module = getattr(self, selected_interface, None)

            if interface_module:
                # Remove the current interface widget if it exists
                if self.current_interface:
                    self.current_interface.pack_forget()  # Unpack the current interface widget

                # Create and display the new interface widget
                self.current_interface = interface_module.Interface(self.interface_wireframe)
                self.current_interface.pack(fill='both', expand=True)

    def clear_main_window(self):
        # Clear all widgets from the main window
        for widget in self.main_window.winfo_children():
            widget.pack_forget()  # Unpack the widget from main_window

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
