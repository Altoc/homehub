#TODO: Fix email notifications for bills
#TODO: Set subject of emails
#TODO: limit input boxes for password settings
#TODO: Make Pizza Purchase Tracker (have it ask each person who bought pizza last to confirm)
#TODO: Have notes frame scroll, takes a bit of tinkering with tkinter to do this
import tkinter
import datetime
from tkinter import *
from tkinter import messagebox
import homehubdb
import hh_email
import hh_date_selector

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
        self.keypadFrame.pack(side = BOTTOM)
        self.passwFrame.pack(side = BOTTOM)
        greeting1 = Label(self.usernameFrame, text="HOME HUB 6270")
        greeting1.config(font=("Times", 32, "bold"))
        greeting1.grid()
        greeting2 = Label(self.usernameFrame, text="Please Login...")
        greeting2.config(font=("Times", 16, "italic"))
        greeting2.grid()
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT name, id FROM users")
        loginUserCounter = 2
        for val in db.cursor.fetchall():
            dbUsername = StringVar()
            dbUsername.set(val[0])
            userButton = Button(self.usernameFrame, textvariable = dbUsername, command=lambda dbUsername=dbUsername: self.userSelect(dbUsername))
            userButton.config(width=16)
            userButton.grid(row=loginUserCounter, column=0)
            # V cursor.execute returns an int of affected rows V
            unreadCheck = db.cursor.execute("SELECT noteID, unread FROM userNotes WHERE userID=%s AND unread=1", (val[1]))
            if(unreadCheck > 0):
                unreadMessages = Label(self.usernameFrame, text="!")
                unreadMessages.config(width=16,font=("Helvetica", 16, "bold"))
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
                passwordNumpad.config(height=2, width=2)
                numCounter = numCounter + 1
                passwordNumpad.grid(row=i, column=j)
                root.update()
        zeroButton = Button(self.keypadFrame, text="0", command=lambda : self.userAuthentication("0"))
        zeroButton.config(height=2, width=2)
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
        self.homeRoot.pack(side=TOP)
        self.menuFrame = Frame(root)
        self.menuFrame.pack(side=TOP)
        self.notesFrame = Frame(root)
        self.notesFrame.pack(side=BOTTOM)
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
        greeting.config(font=("Times", 16, "italic"))
        greeting.grid(row=0,column=2)

        groceryButton = Button(self.menuFrame, text="Grocery List", command=lambda : self.grocery())
        groceryButton.config(height=2,width=12)
        groceryButton.grid(row=1,column=0)

        notesButton = Button(self.menuFrame, text="Leave a Note", command=lambda : self.notes())
        notesButton.config(height=2,width=12)
        notesButton.grid(row=1,column=1)

        self.settingsButton = Button(self.menuFrame, text="Account Settings", command=self.settings)
        self.settingsButton.config(height=2,width=12)
        self.settingsButton.grid(row=1,column=2)

        self.billsButton = Button(self.menuFrame, text="Bill Manager", command=self.billManager)
        self.billsButton.config(height=2,width=12)
        self.billsButton.grid(row=1,column=3)

        self.backToLogin = Button(self.menuFrame, text="LOGOUT", command=self.logout)
        self.backToLogin.config(height=2,width=12)
        self.backToLogin.grid(row=2,column=0)

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
        noteTitleLabel = Label(self.notesFrame, text="A note for you...")
        noteTitleLabel.config(font=("Times",16,"italic"))
        noteTitleLabel.grid()
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

    def billManager(self):
        global mainApp
        global root
        for element in root.winfo_children():
            element.destroy()
        mainApp = FR_billManager(self.username)

class FR_grocery:
    def __init__(self, username):
        global root
        root.title("Groceries")
        self.grocRoot = Frame(root)
        self.listFrame = Frame(root)
        self.entryFrame = Frame(root)
        self.grocRoot.pack(side=TOP)
        self.listFrame.pack()
        self.entryFrame.pack()
        self.username = username
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT id FROM users WHERE name=%s", (self.username))
        dbReturn = db.cursor.fetchall()
        for val in dbReturn:
            self.userID = val[0]
        db.disconnect()
        greeting = Label(self.grocRoot, text = "{}'s Grocery List".format(self.username))
        greeting.config(font=("Times",16,"bold"))
        greeting.grid()
        self.populateGroceryList()
        self.populateUI()

    def populateGroceryList(self):
        for element in self.listFrame.winfo_children():
            element.destroy()
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT item FROM groceryList WHERE userID=%s", (self.userID))
        cntr = 0;
        colCntr = 0;
        for val in db.cursor.fetchall():
            dbGroceryItem = StringVar()
            dbGroceryItem.set(val[0])
            groceryItem = Label(self.listFrame, textvariable=dbGroceryItem)
            deleteItemButton = Button(self.listFrame, text="Delete", 
                command=lambda itemToDel=dbGroceryItem.get(): self.deleteGroceryItem(itemToDel))
            if(cntr > 9):
                cntr = 0;
                colCntr = colCntr + 2;
            groceryItem.grid(row=cntr,column=colCntr)
            deleteItemButton.grid(row=cntr,column=colCntr + 1)
            cntr = cntr + 1;
        db.disconnect()

    def populateUI(self):
        self.entry_1 = Entry(self.entryFrame)
        self.entry_1.grid(row=0, column=0)

        self.entry_button_1 = Button(self.entryFrame, text="Add Item", command = self.addGroceryItem)
        self.entry_button_1.config(height=1,width=8)
        self.entry_button_1.grid(row=0,column=1)

        self.delete_list_button = Button(self.entryFrame, text="Delete List", command = self.deleteGroceryList)
        self.delete_list_button.config(height=1,width=8)
        self.delete_list_button.grid(row=1,column=0)

        self.email_list_button = Button(self.entryFrame, text="Email List", command = self.emailList)
        self.email_list_button.config(height=1,width=8)
        self.email_list_button.grid(row=2,column=0)

        self.back_button = Button(self.entryFrame, text="Home", command = self.backToHome)
        self.back_button.config(height=1,width=8)
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
        groceryString = str()
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT item FROM groceryList WHERE userID=%s", (self.userID))
        for val in db.cursor.fetchall():
            groceryString += '\n' + val[0]
        emailRecip = str()
        db.cursor.execute("SELECT email FROM users WHERE id=%s", (self.userID))
        for val in db.cursor.fetchall():
            emailRecip = val[0]
        em.setMsg(groceryString)
        em.sendMsg(emailRecip)
        db.disconnect()

    def backToHome(self):
        global mainApp
        global root
        for element in root.winfo_children():
            element.destroy()
        mainApp = FR_home(self.username)

class FR_billManager:
    def __init__(self, username):
        global root
        root.title("Bill Manager")
        self.billRoot = Frame(root)
        self.listFrame = Frame(root)
        self.entryFrame = Frame(root)
        self.billRoot.pack(side=TOP)
        self.listFrame.pack()
        self.entryFrame.pack()
        self.username = username
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT id FROM users WHERE name=%s", (self.username))
        dbReturn = db.cursor.fetchall()
        for val in dbReturn:
            self.userID = val[0]
        db.disconnect()
        greeting = Label(self.billRoot, text = "{}'s Bill Manager".format(self.username))
        greeting.config(font=("Times",16,"bold"))
        greeting.grid()
        self.populateBillList()
        self.populateUI()

    def populateBillList(self):
        for element in self.listFrame.winfo_children():
            element.destroy()
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT id, name, description, totalDue, dueDate FROM bills WHERE userID=%s", (self.userID))
        cntr = 0;
        for val in db.cursor.fetchall():
            dbBillName = StringVar()
            dbBillName.set(val[1] + '\n' + str(val[3]))
            billLabel = Label(self.listFrame, textvariable=dbBillName)
            billLabel.grid(row=cntr,column=0)
            billLabel.config(font=("Times", 12, "bold"))
            cntr += 1
            dbBillDate = StringVar()
            dbBillDate.set(val[4])
            billDateLabel = Label(self.listFrame, textvariable=dbBillDate)
            billDateLabel.grid(row=cntr,column=0)
            billDateLabel.config(font=("Times", 10, "italic"))
            cntr += 1
            dbBillDesc = StringVar()
            dbBillDesc.set(val[2])
            billDescLabel = Label(self.listFrame, textvariable=dbBillDesc)
            billDescLabel.grid(row=cntr,column=0)
            billDescLabel.config(font=("Times", 10, "italic"))
            deleteBillButton = Button(self.listFrame, text="Delete", 
                command = lambda IDToDel=val[0] : self.deleteBill(IDToDel))
            deleteBillButton.grid(row=cntr - 2,column=1)
            cntr += 1
        db.disconnect()

    def populateUI(self):
        self.entry_1 = Entry(self.entryFrame)
        self.entry_1.grid(row=0,column=0)
        self.entry_1.insert(0, 'Title')
        self.entry_2 = Entry(self.entryFrame)
        self.entry_2.grid(row=0,column=1)
        self.entry_2.insert(0, 'Description')
        self.entry_3 = Entry(self.entryFrame)
        self.entry_3.grid(row=0,column=2)
        self.entry_3.insert(0, 'Total Due')
        self.entry_4 = hh_date_selector.dateSelector(self.entryFrame,0,3)

        self.entry_button_1 = Button(self.entryFrame, text="Add Bill", command = self.addBill)
        self.entry_button_1.config(height=1,width=8)
        self.entry_button_1.grid(row=0,column=4)

        self.delete_list_button = Button(self.entryFrame, text="Delete All Bills", command = self.deleteBillList)
        self.delete_list_button.config(height=1,width=12)
        self.delete_list_button.grid(row=1,column=1)

        self.email_list_button = Button(self.entryFrame, text="Send Bill Notices", command = self.emailBillList)
        self.email_list_button.config(height=1,width=12)
        self.email_list_button.grid(row=1,column=2)

        self.back_button = Button(self.entryFrame, text="Home", command = self.backToHome)
        self.back_button.config(height=1,width=8)
        self.back_button.grid(row=1,column=3)

    def addBill(self):
        db = homehubdb.Db_manager()
        db.cursor.execute("INSERT INTO bills(name,description,totalDue,userID,dueDate) VALUES(%s, %s, %s, %s, %s)", (self.entry_1.get(), self.entry_2.get(), self.entry_3.get(), self.userID, datetime.date(2019, self.entry_4.month, int(self.entry_4.dayDDDefMsg.get()))))
        db.hubdb.commit()
        db.disconnect()
        self.entry_1.delete(0, 'end')
        self.entry_2.delete(0, 'end')
        self.entry_3.delete(0, 'end')
        self.populateBillList()

    def deleteBill(self, IDToDel):
        db = homehubdb.Db_manager()
        db.cursor.execute("DELETE FROM bills WHERE id=%s AND userID=%s", (IDToDel, self.userID))
        db.hubdb.commit()
        db.disconnect()
        self.populateBillList()

    def deleteBillList(self):
        db = homehubdb.Db_manager()
        db.cursor.execute("DELETE FROM bills WHERE userID=%s", (self.userID))
        db.hubdb.commit()
        db.disconnect()
        self.populateBillList()

    def emailBillList(self):
        global em
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT email FROM users")
        dbReturn1 = db.cursor.fetchall()
        for val in dbReturn1:
            db.cursor.execute("SELECT name, description, totalDue, dueDate FROM bills WHERE userID=%s", (self.userID))
            dbReturn2 = db.cursor.fetchall()
            strToEmail = ""
            for innerVal in dbReturn2:
                strToEmail += strToEmail + "\n" + str(innerVal[0]) + " " + str(innerVal[1]) + " " + str(innerVal[2]) + " " + str(innerVal[3])
            em.setMsg(strToEmail)
            em.sendMsg(val[0])
            print("Sending email to {}.".format(val[0]));
            #print("Val0:{} \n Val1:{} \n Val2:{} \n Val3:{} \n Val4:{}".format(val[0], val[1], val[2], val[3], val[4]));
        db.disconnect()

    '''
    def notifyBillSubscribers(self):
        self.noticePopup = tkinter.Tk()
        self.noticePopup.wm_title("Send Bill Notices")
        self.userSelectFrame = Frame(self.noticePopup)
        self.noticeMethodFrame = Frame(self.noticePopup)
        self.userSelectFrame.pack(side=TOP)
        self.noticeMethodFrame.pack()
        billPromptLabel = Label(self.userSelectFrame, text="Select Bills")
        billPromptLabel.grid(row=0, column=0)
        self.billsToNotify = []
        db = homehubdb.Db_manager()
        db.cursor.execute("SELECT * FROM bills WHERE userID = %s", (self.userID))
        self.billButtons = []
        billButtonId = 0;
        for val in db.cursor.fetchall():
            self.billButtons.append(Button(self.userSelectFrame, text=val[1], command = lambda idVal = val[0], listVal = self.billsToNotify, buttonId = billButtonId : self.selectBillForNotification(idVal, listVal, buttonId)))
            self.billButtons[billButtonId].grid(row = 1, column = billButtonId)
            billButtonId += 1
        noticePromptLabel = Label(self.userSelectFrame, text="Select Users to Notify")
        noticePromptLabel.grid(row=2, column=0)
        self.usersToNotify = []
        db.cursor.execute("SELECT name, id FROM users")
        self.userButtons = []
        userButtonId = 0;
        for val in db.cursor.fetchall():
            self.userButtons.append(Button(self.userSelectFrame, text=val[0], command = lambda idVal = val[1], listVal = self.usersToNotify, buttonId = userButtonId : self.selectUserForNotification(idVal, listVal, buttonId)))
            self.userButtons[userButtonId].grid(row = 3, column = userButtonId)
            userButtonId += 1
        db.disconnect()
        emailPrompt = Button(self.noticeMethodFrame, text="Email Notices", command = lambda myBillList = self.billsToNotify, myUserList = self.usersToNotify : self.emailBillList(myBillList, myUserList))
        emailPrompt.grid(row=1, column=0)
        smsPrompt = Button(self.noticeMethodFrame, text="SMS Notices", command = lambda myBillsList = self.billsToNotify, myUserList = self.usersToNotify : self.smsBillList(myBillsList, myUserList))
        smsPrompt.grid(row=1, column=1)

    def selectUserForNotification(self, userID, listOfUsers, buttonId):
        if userID not in listOfUsers:
            listOfUsers.append(userID)
            self.userButtons[buttonId].config(relief = 'sunken')
        elif userID in listOfUsers:
            listOfUsers.remove(userID)
            self.userButtons[buttonId].config(relief = 'raised')

    def selectBillForNotification(self, billID, listOfBills, buttonId):
        if billID not in listOfBills:
            listOfBills.append(billID)
            self.billButtons[buttonId].config(relief = 'sunken')
        elif billID in listOfBills:
            listOfBills.remove(billID)
            self.billButtons[buttonId].config(relief = 'raised')

    def emailBillList(self, listOfBills, listOfSubs):
        global em
        db = homehubdb.Db_manager()
        billList = []
        for listOfBillsItr in range(len(listOfBills)):
            print(len(listOfBills))
            print(listOfBillsItr)
            db.cursor.execute("SELECT name, description, totalDue FROM bills WHERE id=%s", (listOfBills[listOfBillsItr]))
            for val in db.cursor.fetchall():
                billList.append(val[0] + "[" + val[1] + "]: >> " + str(val[2]) + " <<" + "\n")
        db.cursor.execute("SELECT id, name, email FROM users")
        for value in db.cursor.fetchall():
            if value[0] in listOfSubs:
                em.setMsg(billList)
                em.sendMsg(value[2])
        db.disconnect()
        '''
    def smsBillList(self, listOfBills, listOfSubs):
        global em
        emailList = []
        db = homehubdb.Db_manager()
#        db.cursor.execute("SELECT item FROM groceryList WHERE userID=%s", (self.userID))
#        for val in db.cursor.fetchall():
#            emailList.append(val[0])
#        emailRecip = str()
#        db.cursor.execute("SELECT email FROM users WHERE id=%s", (self.userID))
#        for val in db.cursor.fetchall():
#            emailRecip = val[0]
#        em.setMsg(emailList)
#        em.sendMsg(emailRecip)
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
