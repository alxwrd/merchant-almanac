import sqlite3


class Database(object):
    class DbFile(object):
        name = "merchants-almanac.db"

    def __init__(self, **kwargs):
        self.conn = sqlite3.connect(self.DbFile.name)
        self.conn.row_factory = sqlite3.Row

        self.database_schema = [
            {
                "name": "oceans",
                "columns": {
                    "name": "text"
                }
            },
            {
                "name": "islands",
                "columns": {
                    "ocean_id": "interger",
                    "name": "text"
                }
            },
            {
                "name": "commodities",
                "columns": {
                    "name": "text"
                }
            },
            {
                "name": "orders",
                "columns": {
                    "commodity_id": "interger",
                    "island_id": "interger",
                    "shop": "text",
                    "price": "interger",
                    "amount": "interger",
                    "order_type": "text",
                    "time_reported": "timestamp"

                }
            },
        ]

        self.validate_database()


    def validate_database(self):
        """Checks the defined database schema against the current

        Given the data in `database_schema`: try to figure out how the current
        database looks, and if it doesn't look how the schema says, update the
        it until it does.

        This has the bonus that is the database is empty, it will create it from
        scratch
        """
        for table in self.database_schema:
            try:
                #Check to see if the table exists
                self.conn.execute("SELECT * FROM {}".format(table["name"]))
            except sqlite3.OperationalError:
                #If it doesn't, add it
                self.add_table(table)
                continue

            #Get the column information for the current table
            current_columns = [
                (col[1], col[2]) #Name, type
                for col in self.conn.execute(
                    "PRAGMA table_info({})".format(table["name"]))]

            for column in table["columns"]: #For the columns in the schema
                if not column in [col[0] for col in current_columns]:
                    #If it doesn't exist in the database: add it
                    self.add_column(table["name"],
                                    column,
                                    table["columns"][column])
        self.conn.commit()


    def add_table(self, table):
        self.conn.execute(
            "CREATE TABLE {} ({})".format(
                table["name"],
                ", ".join(["{} {}".format(key, value)
                           for key, value in table["columns"].items()])
            )
        )


    def add_column(self, table, column, type_):
        self.conn.execute("ALTER TABLE {} ADD {} {}".format(table, column, type_))
