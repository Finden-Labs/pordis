import tkinter as tk
from snip_engine import SnippetEngine
from snippets import get_snippets
from tkinter import ttk
from PIL import ImageTk, Image  
from tkinter.messagebox import showinfo

root = tk.Tk()  
root.title('Go Crazy!')
frame = tk.Frame(root)

frame.grid(row = 0, column = 0, sticky="NSEW")
canvas = tk.Canvas(frame, width=600, height=600)  
canvas.pack()  
img = ImageTk.PhotoImage(Image.open("/home/sba/projects/pordis/_build/png/optical_illusion.png"))  
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
button = tk.Button(frame, text = "Apply", command = set,
                fg = "red",
                bd = 2, bg = "light blue", relief = "groove")
button.pack(pady = 5)



def apply_snippet(event):
    selected = event.widget.get()
    if selected != 'Filter':
        all_snips = get_snippets()
        selected_val = all_snips[selected]
        snip.do_snippet(selected_val)
        showinfo(
            title='Result',
            message=f'You selected {selected}!'
        )
# to do -- dont just make snippet, overlay it on original png
# display to user
# allow user to save
# allow user to send (auto saves serverside)
picklist.bind('<<ComboboxSelected>>', apply_snippet)
root.mainloop()