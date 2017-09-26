from Database import Database


class Almanac(Database):

    def __init__(self):
        super().__init__()


    @property
    def oceans(self):
        return [Ocean(row) for row in self.conn.execute("SELECT * FROM oceans")]





class Ocean(Database):

    def __init__(self, id_, name):
        super().__init__()
        self.id_ = id_
        self.name = name


    @property
    def islands(self):
        return [
            Island(row) for row in self.conn.execute(
                "SELECT * FROM islands WHERE ocean_id=?", self.id_)
                ] 




class Island(Database):

    def __init__(self, id_, name, ocean_id):
        super().__init__()
        self.id = id_
        self.name = name
        self.ocean_id = ocean_id


    @property
    def commodities(self):
        return [
            Commodity(row) for row in self.conn.execute(
                "SELECT * FROM commodities WHERE island_id=?", self.id_)
                ] 




class Commodity(Database):

    def __init__(self, id_, name, island_id):
        super().__init__()
        self.id_ = id_
        self.name = name
        self.island_id = island_id
        self.type


    @property
    def buy_orders(self):
        return [
            Order(row) for row in self.conn.execute(
                "SELECT * FROM orders WHERE commodity_id=? AND order_type='Buy'", self.id_)
                ]


    @property
    def sell_orders(self):
        return [
            Order(row) for row in self.conn.execute(
                "SELECT * FROM orders WHERE commodity_id=? AND order_type='Sell'", self.id_)
                ]




class Order(Database):

    def __init__(self, shop, price, amount, order_type):
        super().__init__()
        self.shop = shop
        self.price = price
        self.amount = amount
        self.order_type = order_type