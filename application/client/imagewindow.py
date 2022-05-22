from tkinter import *  
from tkinter.ttk import *
from PIL import ImageTk, Image  

root = Tk()  
root.title('Go Crazy!')
canvas = Canvas(root, width = 475, height = 466)  
canvas.pack()  
img = ImageTk.PhotoImage(Image.open("/home/sba/projects/pordis/application/client/ball.png"))  
canvas.create_image(20, 20, anchor=NW, image=img) 
root.mainloop()