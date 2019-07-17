#TODO: Set subject of emails
#TODO: limit input boxes for password settings
#TODO: Make Pizza Purchase Tracker (have it ask each person who bought pizza last to confirm)
import tkinter
from tkinter import *
from tkinter import messagebox
import homehubdb
import hh_email

#GLOBALS
em = hh_email.EmailManager()
root = tkinter.Tk()
root.attributes('-fullscreen', True)

class FR_login:
    def __init__(self):
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
        greeting.grid(row=0, column=0)
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT name, id FROM users")
        loginUserCounter = 1
        for val in db.cursor.fetchall():
            dbUsername = StringVar()
            dbUsername.set(val[0])
            userButton = Button(self.usernameFrame, textvariable = dbUsername, command=lambda dbUsername=dbUsername: self.userSelect(dbUsername))
            userButton.grid(row=loginUserCounter, column=0)
            # V cursor.execute returns an int of affected rows V
            unreadCheck = db.cursor.execute("SELECT noteID, unread FROM userNotes WHERE userID=%s AND unread=1", (val[1]))
            if(unreadCheck > 0):
                unreadMessages = Label(self.usernameFrame, text="*NEW NOTES*")
                unreadMessages.grid(row=loginUserCounter, column=1)
            loginUserCounter = loginUserCounter + 1
        db.disconnect()
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
        global root
        global mainApp
        if len(self.attemptedPassword) < 3:
            self.attemptedPassword += numToAppend
            self.shownAttemptedPassw_var.set(self.attemptedPassword)
        elif len(self.attemptedPassword) < 4:
            self.attemptedPassword += numToAppend
            self.shownAttemptedPassw_var.set(self.attemptedPassword)
            db = homehubdb.Db_manager()
            db.cursor.execute("SELECT password FROM users WHERE name=%s",  (self.usernameSelected))
            dbReturn = db.cursor.fetchall()
            for val in dbReturn:
                passW = val[0]
            db.disconnect()
            if passW == int(self.attemptedPassword):
                for element in root.winfo_children():
                    element.destroy()
                mainApp = FR_home(self.usernameSelected)
            else:
                self.shownAttemptedPassw_var.set("Wrong... Try Again")
            self.attemptedPassword = str()

class FR_home:
    def __init__(self, username):
        global root
        self.homeRoot = Frame(root)
        self.homeRoot.grid()
        self.notesFrame = Frame(root)
        self.notesFrame.grid()
        root.title("Home")
        self.username = username
        self.populateUI()
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT id FROM users WHERE name=%s", (self.username))
        dbReturn = db.cursor.fetchall()
        for val in dbReturn:
            self.userID = val[0]
        db.disconnect()
        self.populateNotes()

    def populateUI(self):
        greeting = Label(self.homeRoot, text = "Welcome to HomeHub6270, {}".format(self.username))
        greeting.grid()
        groceryButton = Button(self.homeRoot, text="Grocery List", command=lambda : self.grocery())
        groceryButton.grid()
        notesButton = Button(self.homeRoot, text="Leave a Note", command=lambda : self.notes())
        notesButton.grid()
        self.settingsButton = Button(self.homeRoot, text="Account Settings", command=self.settings)
        self.settingsButton.grid()
        self.backToLogin = Button(self.homeRoot, text="LOGOUT", command=self.logout)
        self.backToLogin.grid()

    def logout(self):
        global root
        for element in root.winfo_children():
            element.destroy()
        mainApp = FR_login()

    def notes(self):
        self.notesPopup = tkinter.Tk()
        self.notesPopup.wm_title("Leave A Note")
        notesPrompt = Label(self.notesPopup, text="What would you like to say?")
        notesPrompt.grid()
        self.notesEntry = Entry(self.notesPopup)
        self.notesEntry.grid()
        notesEntry_button = Button(self.notesPopup, text="Say It!", command=self.addNote)
        notesEntry_button.grid()

    def addNote(self):
        db = homehubdb.Db_manager()
        db.cursor.execute("INSERT INTO notes(message,name,dateCreated) VALUES(%s, %s, NOW())", (self.notesEntry.get(), self.username))
        db.cursor.execute("SET @note_id=LAST_INSERT_ID()")
        db.cursor.execute("SELECT id FROM users")
        for val in db.cursor.fetchall():
            db.cursor.execute("INSERT INTO userNotes(userID, noteID) VALUES(%s, @note_id)", (val[0]))
        db.hubdb.commit()
        self.notesEntry.delete(0, 'end')
        db.disconnect()
        self.notesPopup.destroy()
        self.populateNotes()

    #also clears database of expired notes
    def populateNotes(self):
        for element in self.notesFrame.winfo_children():
            element.destroy()
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT id FROM notes WHERE dateCreated BETWEEN NOW() - INTERVAL 14 DAY AND NOW() - INTERVAL 7 DAY")
        for val in db.cursor.fetchall():
            db.cursor.execute("DELETE FROM userNotes WHERE noteID=%s", (val[0]))
            db.cursor.execute("DELETE FROM notes WHERE id=%s", (val[0]))
        db.hubdb.commit()
        db.cursor.execute("SELECT name, message, dateCreated, id FROM notes WHERE dateCreated BETWEEN NOW() - INTERVAL 7 DAY AND NOW()")
        for val in db.cursor.fetchall():
            notedb = StringVar()
            notedb.set(val[1])
            messageAuthor = StringVar()
            messageAuthor.set(val[0])
            dateOfNote = StringVar()
            dateOfNote.set(val[2])
            noteLabel = Label(self.notesFrame, textvariable=notedb)
            noteLabel.grid(column=0)
            authorLabel = Label(self.notesFrame, textvariable=messageAuthor)
            authorLabel.grid(column=1)
            dateLabel = Label(self.notesFrame, textvariable=dateOfNote)
            dateLabel.grid(column=1)
            db.cursor.execute("UPDATE userNotes SET unread=0 WHERE userID=%s AND noteID=%s", (self.userID, val[3]));
        db.hubdb.commit()
        db.disconnect()

    def grocery(self):
        global mainApp
        global root
        for element in root.winfo_children():
            element.destroy()
        mainApp = FR_grocery(self.username)

    def settings(self):
        global mainApp
        global root
        for element in root.winfo_children():
            element.destroy()
        mainApp = FR_settings(self.username)

class FR_grocery:
    def __init__(self, username):
        global root
        self.grocRoot = Frame(root)
        root.title("Groceries")
        self.listFrame = Frame(root)
        self.entryFrame = Frame(root)
        self.grocRoot.grid()
        self.listFrame.grid()
        self.entryFrame.grid()
        self.username = username
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT id FROM users WHERE name=%s", (self.username))
        dbReturn = db.cursor.fetchall()
        for val in dbReturn:
            self.userID = val[0]
        db.disconnect()
        greeting = Label(self.grocRoot, text = "{}'s Grocery List".format(self.username))
        greeting.grid()
        self.populateGroceryList()
        self.populateUI()

    def populateGroceryList(self):
        for element in self.listFrame.winfo_children():
            element.destroy()
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT item FROM groceryList WHERE userID=%s", (self.userID))
        cntr = 0;
        for val in db.cursor.fetchall():
            dbGroceryItem = StringVar()
            dbGroceryItem.set(val[0])
            groceryItem = Label(self.listFrame, textvariable=dbGroceryItem)
            groceryItem.grid(row=cntr,column=0)
            deleteItemButton = Button(self.listFrame, text="Delete", 
                command=lambda itemToDel=dbGroceryItem.get(): self.deleteGroceryItem(itemToDel))
            deleteItemButton.grid(row=cntr,column=1)
            cntr = cntr + 1;
        db.disconnect()

    def populateUI(self):
        self.entry_1 = Entry(self.entryFrame)
        self.entry_1.grid(row=0, column=0)
        self.entry_button_1 = Button(self.entryFrame, text="Add Item", command = self.addGroceryItem)
        self.entry_button_1.grid(row=0,column=1)
        self.delete_list_button = Button(self.entryFrame, text="Delete List", command = self.deleteGroceryList)
        self.delete_list_button.grid(row=1,column=0)
        self.email_list_button = Button(self.entryFrame, text="Email List", command = self.emailList)
        self.email_list_button.grid(row=2,column=0)
        self.back_button = Button(self.entryFrame, text="Back To Home", command = self.backToHome)
        self.back_button.grid(row=3,column=0)

    def addGroceryItem(self):
        db = homehubdb.Db_manager()
        db.cursor.execute("INSERT INTO groceryList(userID,item) VALUES(%s, %s)", (self.userID, self.entry_1.get()))
        db.hubdb.commit()
        db.disconnect()
        self.entry_1.delete(0, 'end')
        self.populateGroceryList()

    def deleteGroceryItem(self, itemToDel):
        db = homehubdb.Db_manager()
        db.cursor.execute("DELETE FROM groceryList WHERE item=%s AND userID=%s", (itemToDel, self.userID))
        db.hubdb.commit()
        db.disconnect()
        self.populateGroceryList()

    def deleteGroceryList(self):
        db = homehubdb.Db_manager()
        db.cursor.execute("DELETE FROM groceryList WHERE userID=%s", (self.userID))
        db.hubdb.commit()
        db.disconnect()
        self.populateGroceryList()

    def emailList(self):
        global em
        emailList = []
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT item FROM groceryList WHERE userID=%s", (self.userID))
        for val in db.cursor.fetchall():
            emailList.append(val[0])
        emailRecip = str()
        db.cursor.execute("SELECT email FROM users WHERE id=%s", (self.userID))
        for val in db.cursor.fetchall():
            emailRecip = val[0]
        em.setMsg(emailList)
        em.sendMsg(emailRecip)
        db.disconnect()

    def backToHome(self):
        global mainApp
        global root
        for element in root.winfo_children():
            element.destroy()
        mainApp = FR_home(self.username)

class FR_settings():
    def __init__(self, username):
        global root
        root.title("Settings")
        self.username = username
        self.settingsRoot = Frame(root)
        self.settingsRoot.grid()
        self.accountInfoFrame = Frame(root)
        self.accountInfoFrame.grid()
        self.populateAccountInfo()

    def populateAccountInfo(self):
        for element in self.accountInfoFrame.winfo_children():
            element.destroy()
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT * FROM users WHERE name=%s", (self.username))
        for val in db.cursor.fetchall():
            session_id = val[0]		#INT
            session_name = val[1]	#str
            session_password = val[2]	#INT
            session_email = val[3]	#str
            session_phone = val[4]	#str
        db.disconnect()
        packedSettingsStr = "Your Account Number: " + str(session_id) + '\n' + \
                            "Your Preferred Name: " + session_name + '\n' + \
                            "Your Primary Email: " + session_email + '\n' + \
                            "Your Primary Cellphone: " + session_phone
        packedSettingsStrVar = StringVar()
        packedSettingsStrVar.set(packedSettingsStr)
        accountSettingsInfoLabel = Label(self.accountInfoFrame, textvariable=packedSettingsStrVar)
        accountSettingsInfoLabel.grid()
        self.populateUI()

    def populateUI(self):
        updateSettingsButton = Button(self.accountInfoFrame, text="Update My Info", command=self.createInfoPrompt)
        updateSettingsButton.grid()
        self.back_button = Button(self.accountInfoFrame, text="Back To Home", command = self.backToHome)
        self.back_button.grid()

    def createInfoPrompt(self):
        self.infoPopup = tkinter.Tk()
        self.infoPopup.wm_title("Update My Information")
        passInfoLabel = Label(self.infoPopup, text="PASSWORDS MUST BE 4 DIGIT NUMBER COMBOS \n MUST CHANGE DB VALUE IF YOU ADDED SOMETHING ELSE")
        passInfoLabel.grid(row=0, column=0)
        passPrompt = Label(self.infoPopup, text="Update Password")
        passPrompt.grid(row=1, column=0)
        self.passEntry = Entry(self.infoPopup)
        self.passEntry.grid(row=1, column=1)
        emailPrompt = Label(self.infoPopup, text="Update Email")
        emailPrompt.grid(row=2, column=0)
        self.emailEntry = Entry(self.infoPopup)
        self.emailEntry.grid(row=2, column=1)
        phonePrompt = Label(self.infoPopup, text="Update Phone")
        phonePrompt.grid(row=3, column=0)
        self.phoneEntry = Entry(self.infoPopup)
        self.phoneEntry.grid(row=3, column=1)
        infoEntry_button = Button(self.infoPopup, text="Update", command=lambda : self.updateInfo())
        infoEntry_button.grid()

    def updateInfo(self):
        db = homehubdb.Db_manager()

        if len(self.passEntry.get()) != 0:
            executeStmt = int(str(self.passEntry.get()))
            db.cursor.execute("UPDATE users SET password=%s WHERE name=%s", (executeStmt, self.username))
        if len(self.emailEntry.get()) != 0:
            executeStmt = str(self.emailEntry.get())
            db.cursor.execute("UPDATE users SET email=%s WHERE name=%s", (executeStmt, self.username))
        if len(self.phoneEntry.get()) != 0:
            executeStmt = str(self.phoneEntry.get())
            db.cursor.execute("UPDATE users SET phone=%s WHERE name=%s", (executeStmt, self.username))

        db.hubdb.commit()
        db.disconnect()
        self.passEntry.delete(0, 'end')
        self.emailEntry.delete(0, 'end')
        self.phoneEntry.delete(0, 'end')
        self.infoPopup.destroy()
        self.populateAccountInfo()

    def backToHome(self):
        global mainApp
        global root
        for element in root.winfo_children():
            element.destroy()
        mainApp = FR_home(self.username)

# MAIN
mainApp = FR_login()
root.mainloop()
