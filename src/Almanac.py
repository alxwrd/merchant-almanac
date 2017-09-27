import maya

from Database import Database


class Almanac(Database):

    def __init__(self):
        super().__init__()

    def update(self, marketdata):
        ocean_id = self.create_or_get_ocean(marketdata["ocean"])
        island_id = self.create_or_get_island(marketdata["island"], ocean_id)

        commodities = marketdata["goods"]

        for commodity in commodities:
            commodity_id = self.create_or_get_commodity(commodity, island_id)

            for order in commodities[commodity]["buy_orders"]:
                self.add_order(order, commodity_id, "buy")

            for order in commodities[commodity]["sell_orders"]:
                self.add_order(order, commodity_id, "sell")

        self.conn.commit()

    def create_or_get_ocean(self, ocean_name):
        ocean = empty = object()

        for ocean in self.conn.execute("SELECT rowid FROM oceans WHERE name=?", (ocean_name,)):
            id_ = ocean["rowid"]

        if ocean is empty:
            cur = self.conn.execute(
                "INSERT INTO oceans VALUES (?)", (ocean_name,))
            id_ = cur.lastrowid

        return id_

    def create_or_get_island(self, island_name, ocean_id):
        island = empty = object()

        for island in self.conn.execute(
                "SELECT rowid FROM islands WHERE name=? AND ocean_id=?",
                (island_name, ocean_id,)):
            id_ = island["rowid"]

        if island is empty:
            cur = self.conn.execute(
                "INSERT INTO islands (name, ocean_id) VALUES (?, ?)",
                (island_name, ocean_id,))
            id_ = cur.lastrowid

        return id_

    def create_or_get_commodity(self, commodity_name, island_id):
        commodity = empty = object()

        for commodity in self.conn.execute(
                "SELECT rowid FROM commodities WHERE name=? AND island_id=?",
                (commodity_name, island_id,)):
            id_ = commodity["rowid"]

        if commodity is empty:
            cur = self.conn.execute(
                "INSERT INTO commodities (name, island_id) VALUES (?, ?)",
                (commodity_name, island_id,))
            id_ = cur.lastrowid

        return id_

    def add_order(self, order, commodity_id, type_):
        self.conn.execute(
            """INSERT INTO orders
                (commodity_id, shop, price, amount, order_type, time_reported)
               VALUES
                (?, ?, ?, ?, ?, ?)""",
            (commodity_id,
             order["shop"],
             order["price"],
             order["amount"],
             type_,
             maya.now().iso8601(),))

    @property
    def oceans(self):
        return {
            row["name"]: Ocean.from_db(row)
            for row in self.conn.execute("SELECT rowid, * FROM oceans")
        }


class Ocean(Database):

    def __init__(self, id_, name):
        super().__init__()
        self.id_ = id_
        self.name = name

    @classmethod
    def from_db(cls, db_row):
        return cls(db_row["rowid"], db_row["name"])

    @property
    def islands(self):
        return {
            row["name"]: Island.from_db(row)
            for row in self.conn.execute(
                "SELECT rowid, * FROM islands WHERE ocean_id=?", (self.id_,))
        }


class Island(Database):

    def __init__(self, id_, name, ocean_id):
        super().__init__()
        self.id_ = id_
        self.name = name
        self.ocean_id = ocean_id

    @classmethod
    def from_db(cls, db_row):
        return cls(db_row["rowid"], db_row["name"], db_row["ocean_id"])

    @property
    def commodities(self):
        return {
            row["name"]: Commodity.from_db(row)
            for row in self.conn.execute(
                "SELECT rowid, * FROM commodities WHERE island_id=?", (self.id_,))
        }

    @property
    def parent(self):
        cur = self.conn.execute("SELECT rowid, * from oceans WHERE rowid=?", (self.ocean_id,))
        return Ocean.from_db(cur.fetchone())


class Commodity(Database):

    def __init__(self, id_, name, island_id):
        super().__init__()
        self.id_ = id_
        self.name = name
        self.island_id = island_id

    @classmethod
    def from_db(cls, db_row):
        return cls(db_row["rowid"], db_row["name"], db_row["island_id"])

    @property
    def buy_orders(self):
        return [
            Order.from_db(row) for row in
            self.conn.execute(
                "SELECT * FROM orders WHERE commodity_id=? AND order_type='buy'",
                (self.id_,))]

    @property
    def sell_orders(self):
        return [
            Order.from_db(row) for row in
            self.conn.execute(
                "SELECT * FROM orders WHERE commodity_id=? AND order_type='sell'",
                (self.id_,))]

    @property
    def parent(self):
        cur = self.conn.execute("SELECT rowid, * from islands WHERE rowid=?", (self.island_id,))
        return Island.from_db(cur.fetchone())


class Order(Database):

    def __init__(self, shop, price, amount, order_type, time_reported, commodity_id):
        super().__init__()
        self.shop = shop
        self.price = price
        self.amount = amount
        self.order_type = order_type
        self.time_reported = time_reported
        self.commodity_id = commodity_id

    @classmethod
    def from_db(cls, db_row):
        return cls(db_row["shop"], db_row["price"], db_row["amount"],
                   db_row["order_type"], db_row["time_reported"],
                   db_row["commodity_id"])

    @property
    def parent(self):
        cur = self.conn.execute("SELECT rowid, * from commodities WHERE rowid=?", (self.commodity_id,))
        return Commodity.from_db(cur.fetchone())
