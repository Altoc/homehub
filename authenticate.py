import tkinter
from tkinter import *
from tkinter import messagebox
import homehubdb

db = homehubdb.Db_manager()

root = tkinter.Tk()
root.geometry("512x512")

usernameFrame = Frame(root)
usernameFrame.pack(sid = TOP)

passwFrame = Frame(root)
passwFrame.pack()

keypadFrame = Frame(root)
keypadFrame.pack(side = BOTTOM)

#GLOBALS
attemptedPassword = str()
shownAttemptedPassw_var = StringVar()
usernameSelected = str()

def passwAttempt(numToAppend):
    global attemptedPassword
    global shownAttemptedPassw_var
    global usernameSelected
    if len(attemptedPassword) < 3:
        print("Entering Num: {}".format(numToAppend))
        attemptedPassword += numToAppend
        shownAttemptedPassw_var.set(attemptedPassword)
    elif len(attemptedPassword) < 4:
        print("Entering Num: {}".format(numToAppend))
        attemptedPassword += numToAppend
        shownAttemptedPassw_var.set(attemptedPassword)
        print("Checking DB for pass for {}".format(usernameSelected))
        db.cursor.execute("SELECT password FROM users WHERE name=%s",  (usernameSelected))
        dbReturn = db.cursor.fetchall()
        for val in dbReturn:
            passW = val[0]
        print("Here is %s 's password: " % (usernameSelected))
        print(passW)
        print("Here is what you entered: %s" % (attemptedPassword))
        if passW == attemptedPassword:
            print("password match!")
            #go to home page for usernameSelected
        else:
            print("passwords did not match")
            #show a "try again" label
        attemptedPassword = str()
    root.update() #update page

def userSelect(usernameClicked):
    global usernameSelected
    usernameSelected = usernameClicked.get()

    numCounter = 1
    for i in range(3):
        for j in range(3):
            numCounterStr = str(numCounter)
            passwordNumpad = Button(keypadFrame, text=numCounterStr, command=lambda numCounterStr=numCounterStr: passwAttempt(numCounterStr)) #passwAttempt("0")) #making this a lambda allows passing of params
            passwordNumpad.config(height=4, width=4)
            numCounter = numCounter + 1
            passwordNumpad.grid(row=i, column=j)
            root.update()
    zeroButton = Button(keypadFrame, text="0", command=lambda : passwAttempt("0"))
    zeroButton.config(height=4, width=4)
    zeroButton.grid(row=4, column=1)

db.cursor.execute("SELECT name FROM users")

for val in db.cursor.fetchall():
    dbUsername = StringVar()
    dbUsername.set(val[0])
    userButton = Button(usernameFrame, textvariable = dbUsername, command=lambda dbUsername=dbUsername: userSelect(dbUsername))
    userButton.grid()

shownAttemptedPassw = Label(passwFrame, textvariable = shownAttemptedPassw_var)
shownAttemptedPassw_var.set(attemptedPassword)
shownAttemptedPassw.grid()

root.mainloop()
