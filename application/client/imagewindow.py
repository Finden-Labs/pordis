import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image  
from tkinter.messagebox import showinfo

root = tk.Tk()  
root.title('Go Crazy!')
frame = tk.Frame(root)


frame.grid(row = 0, column = 0, sticky="NSEW")
canvas = tk.Canvas(frame, width=600, height=600)  
canvas.pack()  
img = ImageTk.PhotoImage(Image.open("/home/sba/projects/pordis/application/client/ball.png"))  
canvas.create_image(300, 300, image=img)  # x,y should be a ratio of canvas width/height

frame.grid(row = 1, column = 0,sticky = "NESW")
snippet_list = ["Arc", "Ellipse", "Gradient", "Spiral", "Text"]
selected_snippet = tk.StringVar()
picklist = ttk.Combobox(frame, values = snippet_list, state = "readonly", textvariable=selected_snippet)
picklist.set("Filter")

picklist.pack(padx = 5, pady = 5)

frame.grid(row = 1, column = 1, sticky = "W")
button = tk.Button(frame, text = "Apply", command = set,
                fg = "red",
                bd = 2, bg = "light blue", relief = "groove")
button.pack(pady = 5)

def apply_snippet(event):
    showinfo(
        title='Result',
        message=f'You selected {selected_snippet.get()}!'
    )

picklist.bind('<<ComboboxSelected>>', apply_snippet)
root.mainloop()