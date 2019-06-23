#TODO: Set subject of grocery emails
import tkinter
from tkinter import *
from tkinter import messagebox
import homehubdb
import hh_grocery
import hh_email

#GLOBALS
db = homehubdb.Db_manager()
em = hh_email.EmailManager()
root = tkinter.Tk()
root.attributes('-fullscreen', True)

class FR_login:
    def __init__(self):
        global db
        global root
        root.title("Login")
        self.usernameFrame = Frame(root)
        self.passwFrame = Frame(root)
        self.keypadFrame = Frame(root)
        self.attemptedPassword = str()
        self.shownAttemptedPassw_var = StringVar()
        self.usernameSelected = str()
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

    def userSelect(self, usernameClicked):
        global root
        self.usernameSelected = usernameClicked.get()
        numCounter = 1
        for i in range(3):
            for j in range(3):
                numCounterStr = str(numCounter)
                passwordNumpad = Button(self.keypadFrame, text=numCounterStr, command=lambda numCounterStr=numCounterStr: self.userAuthentication(numCounterStr)) #making this a lambda allows passing of params
                passwordNumpad.config(height=4, width=4)
                numCounter = numCounter + 1
                passwordNumpad.grid(row=i, column=j)
                root.update()
        zeroButton = Button(self.keypadFrame, text="0", command=lambda : self.userAuthentication("0"))
        zeroButton.config(height=4, width=4)
        zeroButton.grid(row=4, column=1)

    def userAuthentication(self, numToAppend):
        global db
        global root
        global mainApp
        if len(self.attemptedPassword) < 3:
            self.attemptedPassword += numToAppend
            self.shownAttemptedPassw_var.set(self.attemptedPassword)
        elif len(self.attemptedPassword) < 4:
            self.attemptedPassword += numToAppend
            self.shownAttemptedPassw_var.set(self.attemptedPassword)
            db.cursor.execute("SELECT password FROM users WHERE name=%s",  (self.usernameSelected))
            dbReturn = db.cursor.fetchall()
            for val in dbReturn:
                passW = val[0]
            print("Here is %s 's password: " % (self.usernameSelected))
            print(passW)
            print("Here is what you entered: %s" % (self.attemptedPassword))
            if passW == self.attemptedPassword:
                print("password match!")
                for element in root.winfo_children():
                    element.destroy()
                mainApp = FR_home(self.usernameSelected)
            else:
                print("passwords did not match")
                self.shownAttemptedPassw_var.set("Wrong... Try Again")
            self.attemptedPassword = str()

class FR_home:
    def __init__(self, username):
        global root
        self.homeRoot = Frame(root)
        self.homeRoot.grid()
        root.title("Home")
        self.username = username
        greeting = Label(self.homeRoot, text = "Welcome to HomeHub6270, {}".format(self.username))
        greeting.grid()
        groceryButton = Button(self.homeRoot, text="Grocery List", command=lambda : self.grocery())
        groceryButton.grid()
        self.backToLogin = Button(self.homeRoot, text="LOGOUT", command=self.logout)
        self.backToLogin.grid()

    def logout(self):
        global root
        for element in root.winfo_children():
            element.destroy()
        mainApp = FR_login()

    def grocery(self):
        global mainApp
        global root
        for element in root.winfo_children():
            element.destroy()
        mainApp = FR_grocery(self.username)

class FR_grocery:
    def __init__(self, username):
        global db
        global root
        self.grocRoot = Frame(root)
        root.title("Groceries")
        self.listFrame = Frame(root)
        self.entryFrame = Frame(root)
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
        self.back_button = Button(self.entryFrame, text="Back To Home", command = self.backToHome)
        self.back_button.grid()

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
        global em
        emailList = []
        db.cursor.execute("SELECT item FROM GroceryList WHERE id=%s", (self.userID))
        for val in db.cursor.fetchall():
            emailList.append(val[0])
        emailRecip = str()
        db.cursor.execute("SELECT email FROM users WHERE id=%s", (self.userID))
        for val in db.cursor.fetchall():
            emailRecip = val[0]
        em.setMsg(emailList)
        em.sendMsg(emailRecip)

    def backToHome(self):
        global mainApp
        global root
        for element in root.winfo_children():
            element.destroy()
        mainApp = FR_home(self.username)

# MAIN
mainApp = FR_login()

root.mainloop()
