from tkinter import *

class dateSelector:
    def __init__(self, masterFrame, defRow, defCol):	#MasterFrame is tkinter frame/root
        self.monthSelectorFR = Frame(masterFrame)
        self.monthSelectorFR.grid(column=defCol, row=defRow)
        self.daySelectorFR = Frame(masterFrame)
        self.daySelectorFR.bind("<Enter>", self.setDayNum)
        self.daySelectorFR.grid(column=(defCol+1), row=defRow)
        self.days=[]
        self.months=[]
        for y in range(0, 31):
            self.days.append(y + 1)
        for x in range(0, 12):
            self.months.append(x + 1)
        self.day = 1
        self.month = 1
        self.year = 2019
        self.monthDDDefMsg = StringVar()
        self.monthDDDefMsg.set(self.month)
        self.monthDDM = OptionMenu(self.monthSelectorFR, self.monthDDDefMsg, *self.months)
        self.monthDDM.grid()
        self.dayDDDefMsg = StringVar()
        self.dayDDDefMsg.set(self.day)
        self.dayDDM = OptionMenu(self.daySelectorFR, self.dayDDDefMsg, *self.days)
        self.dayDDM.grid()

    def setDayNum(self, event):
        print("setDayNum Triggered")
        self.days.clear()
        if(self.month != int(self.monthDDDefMsg.get())):
            self.month = int(self.monthDDDefMsg.get())
            if(self.month == 2):
                daySize = 28
            elif((self.month < 7) and (self.month % 2 == 1) or (self.month > 7) and (self.month & 2) == 0):
                daySize = 31
            else:
                daySize = 30
            for y in range(0, daySize):
                self.days.append(y + 1)
            om = self.dayDDM["menu"]
            om.delete(0, "end")
            for dayToAdd in self.days:
                om.add_command(label=dayToAdd, 
                                 command=lambda value=dayToAdd: self.dayDDDefMsg.set(value))
