import psycopg2

class Database:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )

    def disconnect(self):
        if self.conn is not None:
            self.conn.close()

    def checkEmail(self, email):
        self.connect()
        cur = self.conn.cursor()
        query = f"SELECT COUNT(*) FROM \"Contractor\" c WHERE c.\"Email\" = '{email}'"
        cur.execute(query)
        result = cur.fetchone()
        cur.close()
        cur1 = self.conn.cursor()
        query1 = f"SELECT COUNT(*) FROM \"AspNetUsers\" a WHERE a.\"Email\" = '{email}' "
        cur1.execute(query1)
        result1=cur1.fetchone()
        cur1.close()
        self.disconnect()
        return result[0] > 0 and result1[0] > 0

    def getUser(self,email):
        self.connect()
        cur = self.conn.cursor()
        query = f"SELECT \"UserName\" FROM \"AspNetUsers\" a WHERE a.\"Email\" = '{email}' "
        cur.execute(query)
        user= cur.fetchone()
        cur.close()
        self.disconnect()
        return user
