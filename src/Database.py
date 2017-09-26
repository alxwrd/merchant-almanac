import sqlite3


class Database(object):
    class DbFile(object):
        name = "merchants-almanac.db"

    def __init__(self, **kwargs):
        self.conn = sqlite3.connect(self.DbFile.name)

        self.database_schema = [
            {
                "table": "oceans",
                "columns": {
                    "id": "interger primary key",
                    "name": "text"
                }
            },
            {
                "table": "islands",
                "columns": {
                    "id": "interger primary key",
                    "ocean_id": "interger",
                    "name": "text"
                }
            },
            {
                "table": "commodities",
                "columns": {
                    "id": "interger primary key",
                    "island_id": "interger",
                    "name": "text"
                }
            },
            {
                "table": "orders",
                "columns": {
                    "id": "interger primary key",
                    "commoditiy_id": "interger",
                    "shop": "text",
                    "price": "interger",
                    "amount": "interger",
                    "order_type": "text"
                }
            },
        ]

        self.validate_database()


    def validate_database(self):
        pass


    def create_database(self):
        for table in self.database_schema:
            self.conn.execute(
                "CREATE TABLE {} ({})".format(
                    table["table"],
                    ", ".join(["{} {}".format(key, value)
                              for key, value in table["columns"].items()])
                )
            )
        self.conn.commit()

    def add_new_data(self, data):
        pass