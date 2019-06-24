import pymysql
print("homehubdb.py called")

#connects to DB on initialization, call disconnect() on object to end connection to db
class Db_manager:
    def __init__(self):
        self.hubdb = pymysql.connect(
            "localhost",
            "root",
            "",
            "homehubdb"
        )
        self.cursor = self.hubdb.cursor()
        print("db connected")

    def disconnect(self):
        if(self.hubdb):
            self.hubdb.close()
            print("db disconnected")
        else:
            print("db was not disconnected")
