import tkinter as tk

class DefaultModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self, text="Open Battery Information", font=('Helvetica', 16))
        label.pack(pady=20)

        message = tk.Label(self, text="Select a module from the sidebar to display its content.")
        message.pack(pady=10)

        info = tk.Label(self, text="This is the default module content.")
        info.pack(pady=10)