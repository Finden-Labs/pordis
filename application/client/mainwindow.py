import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog as fd

from datetime import datetime
import time

class MainWindow():
    def __init__(self, client, font_size):
        self.client = client

        client.window.columnconfigure(0, weight=3) # main window
        client.window.columnconfigure(1, weight=1) # sidebar

        left_frame = ttk.Frame(client.window)
        left_frame.grid(column=0, row=0, sticky="NSEW")
        left_frame.rowconfigure(0, weight=5) # chat window
        left_frame.rowconfigure(1, weight=1) # chat input box (?)
        # left_frame.columnconfigure(0, weight=4)
        # left_frame.columnconfigure(1, weight=1)

        self.user_list = tk.Listbox(client.window) # right sidebar
        self.user_list.grid(column=1, row=0, sticky="NSEW", padx=5, pady=5)

        self.chat_log = ScrolledText(left_frame, state="disabled", font="Courier " + font_size)
        self.chat_log.grid(column=0, row=0, pady=5, padx=5, sticky="NEW")

        self.chat_input = ttk.Entry(left_frame, font="Courier 10")
        self.chat_input.grid(column=0, row=1, pady=5, padx=5, sticky="SEW")
        self.chat_input.bind("<KeyPress>", self.on_input_enter)
        self.chat_input.focus()
    
        def select_file():
            file = fd.askopenfile(
                title='Open Image',
                initialdir='/tmp',
                filetypes=[('image files', '.png')],
                mode='r'
            )
            if file is not None:
                # content = file.read()
                # print(content)
                ws = tk.Toplevel()
                ws.title('Upload Image')
                ws.geometry('400x200')
                pb = ttk.Progressbar(
                    ws, 
                    orient='horizontal', 
                    length=300, 
                    mode='determinate'
                    )
                pb.grid(row=4, columnspan=3, pady=20)
                for i in range(5):
                    ws.update_idletasks()
                    pb['value'] += 20
                    # SEND BINARY FILE!
                    time.sleep(1)
                pb.destroy()
                tk.Label(ws, text='Image Uploaded Successfully!', foreground='green').grid(row=4, columnspan=3, pady=10)

        self.file_button = ttk.Button(
            self.chat_input,
            text='File',
            command=select_file
        )

        self.file_button.grid(column=1, row=0, pady=0, padx=0, sticky="SE")
        self.file_button.pack(expand=True)

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