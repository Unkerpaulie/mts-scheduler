import sqlite3
import streamlit_authenticator as stauth


class User:
    def __init__(self, name, email, password, last_off_day=""):
        self.name = name
        self.email = email
        self.hashedpwd = stauth.Hasher([password]).generate()[0]
        self.last_off_day = last_off_day
        self.params = ':' + ', :'.join(self.__dict__.keys())
        self.tablename = "users"

    
db_file = "users.db"

def create_db():
    qry = """CREATE TABLE IF NOT EXISTS users (
    name text, email text, hashedpwd text, last_off_day text
    )"""

    db = sqlite3.connect(db_file)
    cur = db.cursor()
    with db:
        cur.execute(qry)
    db.close()


def insert_user(u):
    qry = f"INSERT INTO {u.tablename} VALUES ({u.params})"
    # execute, commit and close
    db = sqlite3.connect(db_file)
    cur = db.cursor()
    with db:
        cur.execute(qry, u.__dict__)
    db.close()


def main():
    create_db()

    users = [
        {"name": "Peter Parker", "email": "pparker@something.com", "password": "spider"},
        {"name": "John Wick", "email": "jwick@something.com", "password": "mydog"},
        {"name": "Fred Sanford", "email": "sandman@something.com", "password": "thejunk"},
    ]

    for user in users:
        u = User(user["name"], user["email"], user["password"])
        insert_user(u)

if __name__ == "__main__":
    main()