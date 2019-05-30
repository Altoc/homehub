import tkinter
from tkinter import *
from tkinter import messagebox
import homehubdb
print("home.py called")

db = homehubdb.Db_manager()

root = tkinter.Tk()
root.geometry("512x512")

def userSelect():
    userInfo = messagebox.showinfo("user", "info")

db.cursor.execute("SELECT name FROM users")

for val in db.cursor.fetchall():
    str = StringVar()
    str.set(val)
    userButton = Button(root, textvariable = str, command = userSelect)
    userButton.place(x = 50, y = 50)
    userButton.pack()

root.mainloop()
