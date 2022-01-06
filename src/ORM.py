import sqlite3

class SQL:
    def __init__(self, database):
        self.name = str(database)
        #                              For compatibility with flask
        self.db = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.db.cursor()

    def create_table(self):
        with self.db:
            return self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS queue (link text UNIQUE, title text, uploader text);"
            )

    def push_to_queue(self, link: str, title: str = "", uploader: str= ""):
        with self.db:
            print(f"push-to-queue: inserting {(link, title, uploader)}")
            return self.cursor.execute(
                "INSERT INTO queue (link, title, uploader) VALUES (?, ?, ?);", (link, title, uploader)
            )

    def fetch_queue(self):
        with self.db:
            return self.cursor.execute(
                "SELECT * FROM queue;"
            ).fetchall()

    def select_last_rowid(self):
        with self.db:
            return self.cursor.execute(
                """SELECT rowid FROM queue;"""
            ).fetchone()

    def delete_rowid(self, rowid: int):
        with self.db:
            return self.cursor.execute(
                """DELETE FROM queue WHERE rowid=?""", rowid
            )