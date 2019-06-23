import tkinter
from tkinter import *
from tkinter import messagebox
import homehubdb
import hh_grocery

#GLOBALS
db = homehubdb.Db_manager()

class FR_login:
    def __init__(self):
        global db
        self.root = tkinter.Tk()
        self.root.title("Login")
        self.usernameFrame = Frame(self.root)
        self.passwFrame = Frame(self.root)
        self.keypadFrame = Frame(self.root)
        self.attemptedPassword = str()
        self.shownAttemptedPassw_var = StringVar()
        self.usernameSelected = str()
        self.root.attributes('-fullscreen', True)
        self.usernameFrame.pack(side = TOP)
        self.passwFrame.pack()
        self.keypadFrame.pack(side = BOTTOM)
        greeting = Label(self.usernameFrame, text="Please Login")
        greeting.grid()
        db.cursor.execute("SELECT name FROM users")
        for val in db.cursor.fetchall():
            dbUsername = StringVar()
            dbUsername.set(val[0])
            userButton = Button(self.usernameFrame, textvariable = dbUsername, command=lambda dbUsername=dbUsername: self.userSelect(dbUsername))
            userButton.grid()
        shownAttemptedPassw = Label(self.passwFrame, textvariable = self.shownAttemptedPassw_var)
        self.shownAttemptedPassw_var.set(self.attemptedPassword)
        shownAttemptedPassw.grid()
        self.root.mainloop()

    def userSelect(self, usernameClicked):
        self.usernameSelected = usernameClicked.get()
        numCounter = 1
        for i in range(3):
            for j in range(3):
                numCounterStr = str(numCounter)
                passwordNumpad = Button(self.keypadFrame, text=numCounterStr, command=lambda numCounterStr=numCounterStr: self.userAuthentication(numCounterStr)) #making this a lambda allows passing of params
                passwordNumpad.config(height=4, width=4)
                numCounter = numCounter + 1
                passwordNumpad.grid(row=i, column=j)
                self.root.update()
        zeroButton = Button(self.keypadFrame, text="0", command=lambda : self.userAuthentication("0"))
        zeroButton.config(height=4, width=4)
        zeroButton.grid(row=4, column=1)

    def userAuthentication(self, numToAppend):
        global db
        global mainApp
        if len(self.attemptedPassword) < 3:
            #print("Entering Num: {}".format(numToAppend))
            self.attemptedPassword += numToAppend
            self.shownAttemptedPassw_var.set(self.attemptedPassword)
        elif len(self.attemptedPassword) < 4:
            #print("Entering Num: {}".format(numToAppend))
            self.attemptedPassword += numToAppend
            self.shownAttemptedPassw_var.set(self.attemptedPassword)
            #print("Checking DB for pass for {}".format(usernameSelected))
            db.cursor.execute("SELECT password FROM users WHERE name=%s",  (self.usernameSelected))
            dbReturn = db.cursor.fetchall()
            for val in dbReturn:
                passW = val[0]
            print("Here is %s 's password: " % (self.usernameSelected))
            print(passW)
            print("Here is what you entered: %s" % (self.attemptedPassword))
            if passW == self.attemptedPassword:
                print("password match!")
                self.root.destroy()	#Destroy login window
                mainApp = FR_home(self.usernameSelected)	#Create Home window
            else:
                print("passwords did not match")
                self.shownAttemptedPassw_var.set("Wrong... Try Again")
            self.attemptedPassword = str()

class FR_grocery:
    def __init__(self, username):
        global db
        self.grocRoot = tkinter.Tk()
        self.grocRoot.title("Groceries")
        self.grocRoot.attributes('-fullscreen', True)
        self.listFrame = Frame(self.grocRoot)
        self.entryFrame = Frame(self.grocRoot)
        self.grocRoot.grid()
        self.listFrame.grid()
        self.entryFrame.grid()

        self.username = username
        greeting = Label(self.grocRoot, text = "{}'s Grocery List".format(self.username))
        greeting.grid()
        db.cursor.execute("SELECT id FROM users WHERE name=%s", (self.username))
        dbReturn = db.cursor.fetchall()
        for val in dbReturn:
            self.userID = val[0]
        print("User ID: {}".format(self.userID))
        self.populateGroceryList()
        self.populateUI()

        self.grocRoot.mainloop()

    def populateGroceryList(self):
        global db
        #clear list frame
        for element in self.listFrame.winfo_children():
            element.destroy()
        db.cursor.execute("SELECT item FROM GroceryList WHERE id=%s", (self.userID))
        for val in db.cursor.fetchall():
            dbGroceryItem = StringVar()
            dbGroceryItem.set(val[0])
            groceryItem = Label(self.listFrame, textvariable=dbGroceryItem)
            groceryItem.grid()

    def populateUI(self):
        global db
        self.entry_1 = Entry(self.entryFrame)
        self.entry_1.grid()
        self.entry_button_1 = Button(self.entryFrame, text="Add Item", command = self.addGroceryItem)
        self.entry_button_1.grid()
        self.email_list_button = Button(self.entryFrame, text="Email List", command = self.emailList)
        self.email_list_button.grid()

    def addGroceryItem(self):
        global db
        print("Adding {} to list...".format(self.entry_1.get()))
        try:
            db.cursor.execute("INSERT INTO GroceryList(id,item) VALUES(%s, %s)", (self.userID, self.entry_1.get()))
            db.hubdb.commit()
            self.entry_1.delete(0, 'end')
            self.populateGroceryList()
        except MySQLError as e:
            print('Got error {!r}, errno is {}'.format(e, e.args[0]))

    def emailList(self):
        global db
        groceryListStr = str()
        db.cursor.execute("SELECT item FROM GroceryList WHERE id=%s", (self.userID))
        for val in db.cursor.fetchall():
            groceryListStr += val[0]
        print(groceryListStr)
        #send email to email in user's DB with that string as the body of the message

class FR_home:
    def __init__(self, username):
        self.homeRoot = tkinter.Tk()
        self.homeRoot.title("Home")
        self.homeRoot.attributes('-fullscreen', True)
        self.username = username
        greeting = Label(self.homeRoot, text = "Welcome to HomeHub6270, {}".format(username))
        greeting.grid()
        groceryButton = Button(self.homeRoot, text="Grocery List", command=lambda : self.grocery())
        groceryButton.grid()
        self.homeRoot.mainloop()

    def grocery(self):
        global mainApp
        self.homeRoot.destroy()
        mainApp = FR_grocery(self.username)

# MAIN
mainApp = FR_login()
