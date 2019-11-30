import smtplib

class EmailManager:
    def __init__(self):
        self.fromAddress = "homehub6270@gmail.com"
        self.toAddress = "altocgamedev@gmail.com"
        self.msg = "This is the default message, home hub be bugging, yo."
        print("Email Manager initialized")

    def setMsg(self, msgToBeSet): #msgtobeset is a list
        myMsg = str()
        for val in msgToBeSet:
            myMsg += val
        self.msg = myMsg
        print("Email Message Set")

    def sendMsg(self, emailRecipient):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login("homehub6270@gmail.com", "gogogogo1")   #second argument is password for email account
        try:
            server.sendmail(
                 self.fromAddress,
                 emailRecipient,
                 self.msg)
            print("Email Sent!")
            server.quit()
        except smtplib.SMTPResponseException as e:
            error_code = e.smtp_code
            error_message = e.smtp_error
        except:
            print("Error: Could not send message.")

