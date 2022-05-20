import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from datetime import datetime

class MainWindow():
    def __init__(self, client, font_size):
        self.client = client

        client.window.columnconfigure(0, weight=3)
        client.window.columnconfigure(1, weight=1)

        left_frame = ttk.Frame(client.window)
        left_frame.grid(column=0, row=0, sticky="NSEW")
        left_frame.rowconfigure(0, weight=5)
        left_frame.rowconfigure(1, weight=1)

        self.user_list = tk.Listbox(client.window)
        self.user_list.grid(column=1, row=0, sticky="NSEW", padx=5, pady=5)

        self.chat_log = ScrolledText(left_frame, state="disabled", font="Courier " + font_size)
        self.chat_log.grid(column=0, row=0, pady=5, padx=5, sticky="NEW")

        self.chat_input = ttk.Entry(left_frame, font="Courier 10")
        self.chat_input.grid(column=0, row=1, pady=5, padx=5, sticky="SEW")
        self.chat_input.bind("<KeyPress>", self.on_input_enter)
        self.chat_input.focus()
    
    def append_to_chat_log(self, text: bytes, system_message=False, timestamp=True):
        self.chat_log.config(state="normal")
        self.chat_log.insert("end", (b"[" + datetime.now().strftime("%d/%m %H:%M:%S").encode("utf-8") + b"] " if timestamp else b"") + (b"*** " + text + b" ***" if system_message else text) + b"\n")
        self.chat_log.config(state="disabled")
        self.chat_log.see("end")
    
    def on_user_list_changed(self):
        self.user_list.delete(0, "end")
        for user in self.client.user_list:
            self.user_list.insert("end", user["username"] + (b" (ID " + str(int.from_bytes(user["unique_id"], "little")).encode("utf-8") + b")" if self.client.user.is_admin else b""))

    def on_input_enter(self, event):
        if event.keysym == "KP_Enter" or event.keysym == "Return":
            if self.client.on_chat_input(self.chat_input.get()):
                self.chat_input.delete(0, "end")