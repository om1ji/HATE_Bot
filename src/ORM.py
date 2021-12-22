import sqlite3

class SQL:
    def __init__(self, database):
        self.name = str(database)
        self.db = sqlite3.connect(database)
        self.cursor = self.db.cursor()

    def create_table(self):
        with self.db:
            return self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS queue (link text UNIQUE, title text, uploader text);"
            )

    def push_to_queue(self, link: str, title: str ="", uploader: str=""):
        with self.db:
            return self.cursor.execute(
                "INSERT INTO queue (link) VALUES (?, ?, ?);", link, title, uploader
            )

    def fetch_queue(self):
        with self.db:
            return self.cursor.execute(
                "SELECT link FROM queue;"
            )

    def select_last_rowid(self):
        with self.db:
            return self.cursor.execute(
                """SELECT rowid FROM queue;"""
            )

    def delete_rowid(self, rowid: int):
        with self.db:
            return self.cursor.execute(
                """DELETE FROM queue WHERE rowid=?""", rowid
            )