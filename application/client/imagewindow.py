import tkinter as tk
import os
from snip_engine import SnippetEngine
from snippets import get_snippets
from tkinter import ttk
from PIL import ImageTk, Image  
from tkinter.messagebox import showinfo
from tkinter.filedialog import asksaveasfile

root = tk.Tk()  
root.title('Go Crazy!')
frame = tk.Frame(root)
img_id = None

frame.grid(row = 0, column = 0, sticky="NSEW")
canvas = tk.Canvas(frame, width=600, height=600)  
canvas.pack()  
img = ImageTk.PhotoImage(Image.open("/home/sba/projects/pordis/application/client/ball.png"))  
canvas.create_image(300, 300, image=img)  # x,y should be a ratio of canvas width/height

frame.grid(row = 1, column = 0,sticky = "NESW")
snip = SnippetEngine()
snippet_dict = get_snippets()
snippet_names = tk.StringVar()
snippet_names = list(snippet_dict.keys())
snippet_values = list(snippet_dict.values())
#snippet_list = ["Arc", "Ellipse", "Gradient", "Spiral", "Text"]
# selected_snippet = tk.StringVar()
picklist = ttk.Combobox(frame, values=snippet_names, state = "readonly", textvariable=snippet_names)
picklist.set("Filter")

picklist.pack(padx = 5, pady = 5)

frame.grid(row = 1, column = 1, sticky = "W")
save_button = tk.Button(frame, text = "Save", command=lambda:save())
save_button.pack(pady = 5)

frame.grid(row = 1, column = 2, sticky = "W")
send_button = tk.Button(frame, text = "Send to Chat", command=set)
send_button.pack(pady = 5)

def apply_snippet(event):
    global img_id
    selected = event.widget.get()
    if selected != 'Filter':
        all_snips = get_snippets()
        selected_val = all_snips[selected]
        img_id = snip.do_snippet(selected_val)
        filename = os.path.join("_build", "png", "%s.png" % img_id)
        modified_img = ImageTk.PhotoImage(Image.open(filename))
        modified_img_container = canvas.create_image(300, 300, image=modified_img)  # x,y should be a ratio of canvas width/height
        canvas.itemconfig(modified_img_container, image=modified_img)
        root.mainloop()
        #showinfo(
        #    title='Result',
        #    message=f'You selected {selected}!'
        #)
def save():
    global img_id
    filename = os.path.join("%s.png" % img_id)
    file_types = [('Image File', '*.png')]
    asksaveasfile(filetypes =  file_types, defaultextension = file_types, initialfile=filename)
    # root.mainloop()
# allow user to save
# allow user to send (auto saves serverside)
picklist.bind('<<ComboboxSelected>>', apply_snippet)
root.mainloop()