import tkinter
from tkinter import *
from tkinter import messagebox
import homehubdb
import hh_email

db = homehubdb.Db_manager()
mailer = hh_email.EmailManager()

root = tkinter.Tk()
root.geometry("512x512")

def emailGroceryList():
    mailer.setMsg(groceryList)
    mailer.sendMsg("altocgamedev@gmail.com") #TODO: make based on user logged in, not hard coded

def grabAndShowList():
    db.cursor.execute("SELECT item FROM GroceryList WHERE id = 0") #TODO: make id not hard-coded, but based on user logged in
    groceryList = []
    for val in db.cursor.fetchall():
        fetchedStr = StringVar()
        fetchedStr.set(val)
        groceryItem = fetchedStr.get()
        groceryList.append(groceryItem)
    for item in groceryList:
        print(item + "\n")

groceryHeader = StringVar()
groceryHeaderLabel = Label(root, textvariable = groceryHeader)
groceryHeader.set("Here is your grocery list: \n")
groceryHeaderLabel.pack()

groceryItems = StringVar()
groceryLabel = Label(root, textvariable = groceryItems)
groceryString = str()
for val in groceryList:
    groceryString += val + "\n"

groceryItems.set(groceryString)
groceryLabel.pack()

mailGroceryButton = Button(root, text = "Email Myself Grocery List", command = emailGroceryList)
mailGroceryButton.pack()

root.mainloop()
