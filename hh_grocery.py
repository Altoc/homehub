import tkinter
from tkinter import *
from tkinter import messagebox
import homehubdb
import hh_email

class GroceryManager():
    def __init__(self, emailAddr):
        self.emailTo = emailAddr
        self.mailer = hh_email.EmailManager()

    def emailGroceryList(self):
        mailer.setMsg(groceryList)
        mailer.sendMsg(self.emailTo)
