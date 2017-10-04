import sqlite3


class Database(object):
    db_file = "merchants-almanac.db"
    __conn = None

    def __init__(self, **kwargs):
        if not Database.__conn:
            Database.__conn = sqlite3.connect(
                Database.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
            Database.__conn.row_factory = sqlite3.Row

        self.conn = self.__conn

        self.database_schema = [
            {
                "name": "oceans",
                "columns": [
                    {"name": "name", "type": "text", "index": False},
                ]
            },
            {
                "name": "islands",
                "columns": [
                    {"name": "ocean_id", "type": "interger", "index": True},
                    {"name": "name", "type": "text", "index": False},
                ]
            },
            {
                "name": "commodities",
                "columns": [
                    {"name": "name", "type": "text", "index": False},
                ]
            },
            {
                "name": "orders",
                "columns": [
                    {"name": "commodity_id", "type": "interger", "index": True},
                    {"name": "island_id", "type": "interger", "index": True},
                    {"name": "shop", "type": "text", "index": False},
                    {"name": "price", "type": "interger", "index": True, "index_dir": "ASC"},
                    {"name": "amount", "type": "interger", "index": False},
                    {"name": "order_type", "type": "text", "index": True},
                    {"name": "time_reported", "type": "timestamp", "index": True, "index_dir": "DESC"},
                ]
            },
        ]


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

            requires_index = [column for column in table["columns"]
                              if column["index"]]
            try:
                self.delete_index(table)
            except sqlite3.OperationalError:
                pass

            if requires_index:
                self.add_index(table, requires_index)

            # current_index = [
            #     (col["name"], col["tbl_name"], col["sql"])
            #     for col in self.conn.execute(
            #         "SELECT * FROM sqlite_master "
            #         "WHERE type = 'index' "
            #         "AND tbl_name = ?", (table["name"],))]

            #Get the column information for the current table
            current_columns = [col for col in self.conn.execute(
                "PRAGMA table_info({})".format(table["name"]))]

            for column in table["columns"]: #For the columns in the schema
                if not column["name"] in (col["name"] for col in current_columns):
                    #If it doesn't exist in the database: add it
                    self.add_column(table["name"],
                                    column)

        self.conn.commit()


    def add_table(self, table):
        self.conn.execute(
            "CREATE TABLE {} ({})".format(
                table["name"],
                ", ".join(["{} {}".format(col["name"], col["type"])
                           for col in table["columns"]])
            )
        )


    def add_column(self, table, column):
        self.conn.execute("ALTER TABLE {} ADD {} {}".format(
            table, column["name"], column["type"]))


    def add_index(self, table, columns):
        self.conn.execute(
            "CREATE INDEX {table}_index ON {table} ({columns});".format(
                table=table["name"],
                columns=", ".join([
                    "{} {}".format(column["name"], column.get("index_dir", ""))
                    for column in columns
                    ])
                )
            )


    def delete_index(self, table):
        self.conn.execute(
            "DROP INDEX {table}_index".format(
                table=table["name"])
            )
