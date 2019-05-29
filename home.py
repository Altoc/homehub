import tkinter
from tkinter import *
import homehubdb
print("home.py called")

db = homehubdb.Db_manager()

root = tkinter.Tk()

myStr = StringVar()
label = Label(root, textvariable = myStr)

db.cursor.execute("SELECT * FROM users")

for val in db.cursor.fetchall():
    myStr.set(val)

label.pack()

root.mainloop()
