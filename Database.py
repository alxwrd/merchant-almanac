import sqlite3



class Database(object):

    def __init__(self):
        self.conn = sqlite3.connect("merchant-almanac.db")




class Ocean(object):

    def __init__(self, id_, name):
        self.id_ = id_
        self.name = name
        self.islands = self.get_islands()


    def get_islands(self, db_conn):
        results = db_conn.excecute("SELECT * FROM islands WHERE id=?", (self.id_))
        return [Island(*result) for result in results.fetchall()]



class Island(object):

    def __init__(self, id_, name):
        self.id = id_
        self.name = name
        self.commodities = self.get_commodities()


    def get_commodities(self, db_conn):
        results = db_conn.excecute("SELECT * FROM commodities WHERE id=?", (self.id_))
        return [Commodity(*result) for result in results]


class Commodity(object):

    def __init__(self, id_, name):
        self.id_ = id_
        self.name = name
        self.buyorders = self.get_buyorders()
        self.sellorders = self.get_sellorders()


    def get_buyorders(self):
        pass


    def get_sellorders(self):
        pass




class Order(object):

    def __init__(self, shop, price, amount):
        self.shop = shop
        self.price = price
        self.amount = amount
