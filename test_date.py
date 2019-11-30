import hh_date_selector
from tkinter import *

root = Tk()
root.attributes('-fullscreen', True)

testFrame = Frame(root)
testFrame.grid()

testDate = hh_date_selector.dateSelector(testFrame)

mainloop()
