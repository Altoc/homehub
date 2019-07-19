import hh_email

mailer = hh_email.EmailManager()
mailer.setMsg("I love my girlfriend Emilee!")
mailer.sendMsg("test@gmail.com")
