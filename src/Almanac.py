import datetime

import maya
import requests
from lxml import html
from fuzzywuzzy import process

from Database import Database


class Almanac(Database):

    def __init__(self):
        super().__init__()
        self.validate_database()


    def update(self, marketdata):
        ocean_id = self.create_or_get_ocean(marketdata["ocean"])

        island_name = self.validate_island(marketdata["ocean"], marketdata["island"])

        island_id = self.create_or_get_island(island_name, ocean_id)

        commodities = marketdata["goods"]

        now = datetime.datetime.now()

        for commodity in commodities:
            commodity_id = self.create_or_get_commodity(commodity)

            for order in commodities[commodity]["buy_orders"]:
                self.add_order(order, commodity_id, island_id, "buy", now)

            for order in commodities[commodity]["sell_orders"]:
                self.add_order(order, commodity_id, island_id, "sell", now)

        self.conn.commit()


    def validate_island(self, ocean_name, island_name):
        page = requests.get("http://{}.puzzlepirates.com/yoweb/"
                            "island/info.wm?showAll=true".format(ocean_name))
        tree = html.fromstring(page.content)

        islands = tree.xpath("//font[@size='+1']/text()")

        return process.extract(island_name, islands, limit=1)[0][0]


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


    def create_or_get_commodity(self, commodity_name):
        commodity = empty = object()

        for commodity in self.conn.execute(
                "SELECT rowid FROM commodities WHERE name=?",
                (commodity_name,)):
            id_ = commodity["rowid"]

        if commodity is empty:
            cur = self.conn.execute(
                "INSERT INTO commodities (name) VALUES (?)",
                (commodity_name,))
            id_ = cur.lastrowid

        return id_


    def add_order(self, order, commodity_id, island_id, type_, time):
        self.conn.execute(
            """INSERT INTO orders
                (commodity_id, island_id, shop, price, amount, order_type, time_reported)
               VALUES
                (?, ?, ?, ?, ?, ?, ?)""",
            (commodity_id,
             island_id,
             order["shop"],
             order["price"],
             order["amount"],
             type_,
             time,))


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


    @property
    def commodities(self):
        return {
            row["name"]: Commodity.from_db(row, parent=self)
            for row in self.conn.execute(
                "SELECT rowid, * FROM commodities WHERE rowid in "
                "(SELECT commodity_id FROM orders WHERE island_id in "
                "(SELECT rowid FROM islands WHERE ocean_id=?))", (self.id_,))
        }


    def orders(self, commodity_id, type_, all_orders):
        orders = [
            Order.from_db(row) for row in
            self.conn.execute(
                ("SELECT * FROM orders o "
                 "WHERE cast(commodity_id as text) like ? AND order_type like ?"),
                (commodity_id, type_,))]

        if all_orders:
            return orders
        else:
            newest = max(orders, key=lambda o: o.time_reported)
            return [order for order in orders if order.time_reported == newest.time_reported]


    def buy_orders(self, commodity_id="%", all_orders=False):
        return self.orders(commodity_id, "buy", all_orders)


    def sell_orders(self, commodity_id="%", all_orders=False):
        return self.orders(commodity_id, "sell", all_orders)


    @property
    def routes(self):
        return []
        orders = {
            order.commodity_name: [
                order
            ]
            for order in self.orders("%", "%", False)
        }
        return orders



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
            row["name"]: Commodity.from_db(row, parent=self)
            for row in self.conn.execute(
                "SELECT rowid, * FROM commodities WHERE rowid in "
                "(SELECT commodity_id FROM orders WHERE island_id=?) ", (self.id_,)
            )
        }


    @property
    def parent(self):
        cur = self.conn.execute("SELECT rowid, * from oceans WHERE rowid=?", (self.ocean_id,))
        return Ocean.from_db(cur.fetchone())


    def orders(self, commodity_id, type_, all_orders, sort):
        orders = self.conn.execute(
            ("SELECT * FROM orders o "
             "WHERE commodity_id = ? AND order_type = ? "
             "AND island_id = ? AND "
             "time_reported = (SELECT MAX(time_reported) "
             "FROM orders WHERE o.commodity_id=orders.commodity_id "
             "AND o.island_id=orders.island_id) ORDER BY price " + sort),
            (commodity_id, type_, self.id_,))
        return orders


    def buy_orders(self, commodity_id="%", all_orders=False, sort="DESC"):
        return self.orders(commodity_id, "buy", all_orders, sort)


    def sell_orders(self, commodity_id="%", all_orders=False, sort="ASC"):
        return self.orders(commodity_id, "sell", all_orders, sort)


    @property
    def routes(self):
        islands = self.parent.islands
        for island in islands:
            commodities = islands[island].commodities
            for commodity in commodities:
                buy_orders = self.sell_orders(commodities[commodity].id_)
                sell_orders = islands[island].buy_orders(commodities[commodity].id_)
                try:
                    for orders in zip(buy_orders, sell_orders):
                        if orders[0]["price"] < orders[1]["price"]:
                            yield Route(
                                self,
                                islands[island],
                                commodities[commodity],
                                Order.from_db(orders[0]),
                                Order.from_db(orders[1]))
                        else:
                            raise StopIteration
                except StopIteration:
                    continue


class Route(object):

    def __init__(self, start_island, end_island, commodity, buy_order, sell_order):
        self.start_island = start_island
        self.end_island = end_island
        self.commodity = commodity
        self.buy_order = buy_order
        self.sell_order = sell_order

    @property
    def difference(self):
        return self.sell_order.price - self.buy_order.price


class Commodity(Database):

    def __init__(self, id_, name, parent):
        super().__init__()
        self.id_ = id_
        self.name = name
        self.parent = parent


    @classmethod
    def from_db(cls, db_row, parent=None):
        return cls(db_row["rowid"], db_row["name"], parent)



class Order(Database):

    def __init__(self, shop, price, amount, order_type, time_reported,
                 island_id, commodity_id):
        super().__init__()
        self.shop = shop
        self.price = price
        self.amount = amount
        self.order_type = order_type
        self.time_reported = time_reported
        self.island_id = island_id
        self.commodity_id = commodity_id


    @property
    def island_name(self):
        cur = self.conn.execute(
            "SELECT name FROM islands WHERE rowid=?", (self.island_id,)
            )
        return cur.fetchone()["name"]


    @property
    def commodity_name(self):
        cur = self.conn.execute(
            "SELECT name FROM commodities WHERE rowid=?", (self.commodity_id,)
            )
        return cur.fetchone()["name"]


    @classmethod
    def from_db(cls, db_row):
        return cls(db_row["shop"], db_row["price"], db_row["amount"],
                   db_row["order_type"], db_row["time_reported"],
                   db_row["island_id"], db_row["commodity_id"])


    @property
    def parent(self):
        cur = self.conn.execute("SELECT rowid, * from islands WHERE rowid=?", (self.island_id,))
        return Commodity.from_db(cur.fetchone())


if __name__ == "__main__":
    al = Almanac()
    for route in al.oceans["Obsidian"].islands["Port Venture"].routes:
        print(route)
