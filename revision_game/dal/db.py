
import sqlite3, os
from pathlib import Path
from .. import settings

try:
    import bcrypt
except Exception:
    bcrypt = None

def _hash_pw(pw: str) -> str:
    if bcrypt:
        try:
            return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
        except Exception:
            pass
    return pw

class DB:
    def __init__(self):
        self.conn = None
        self.cur = None
    def __enter__(self):
        self.conn = sqlite3.connect(settings.DB_PATH)
        self.conn.execute("PRAGMA foreign_keys=ON;")
        self.cur = self.conn.cursor()
        return self
    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.cur.close()
        self.conn.close()
    def q(self, sql, params=()):
        self.cur.execute(sql, params)
        return self.cur
    def one(self):
        return self.cur.fetchone()
    def all(self):
        return self.cur.fetchall()

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS UserTypes(
        UserTypeID INTEGER PRIMARY KEY,
        UserType TEXT NOT NULL UNIQUE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS UserDetails(
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT NOT NULL UNIQUE,
        Password TEXT NOT NULL,
        UserTypeID INTEGER NOT NULL,
        TotalScore INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(UserTypeID) REFERENCES UserTypes(UserTypeID) ON UPDATE CASCADE ON DELETE RESTRICT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Topics(
        TopicID INTEGER PRIMARY KEY,
        Topic TEXT NOT NULL UNIQUE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS GameScores(
        GameID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER NOT NULL,
        TopicID INTEGER NOT NULL,
        Score INTEGER NOT NULL,
        Date TEXT NOT NULL,
        FOREIGN KEY(UserID) REFERENCES UserDetails(UserID) ON DELETE CASCADE,
        FOREIGN KEY(TopicID) REFERENCES Topics(TopicID) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS QuestionStats(
        UserID INTEGER NOT NULL,
        TopicID INTEGER NOT NULL,
        QHash TEXT NOT NULL,
        CorrectCount INTEGER NOT NULL DEFAULT 0,
        WrongCount INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(UserID, TopicID, QHash),
        FOREIGN KEY(UserID) REFERENCES UserDetails(UserID) ON DELETE CASCADE,
        FOREIGN KEY(TopicID) REFERENCES Topics(TopicID) ON DELETE CASCADE
    );
    """ ,
    """
    CREATE TABLE IF NOT EXISTS SchemaVersion(
        Version INTEGER NOT NULL
    );
    """
]

SEED = [
    ("INSERT OR IGNORE INTO UserTypes(UserTypeID, UserType) VALUES (?,?)", (1, "Teacher")),
    ("INSERT OR IGNORE INTO UserTypes(UserTypeID, UserType) VALUES (?,?)", (2, "Student")),
    ("INSERT OR IGNORE INTO Topics(TopicID, Topic) VALUES (?,?)", (1, "Particles and Matter")),
    ("INSERT OR IGNORE INTO Topics(TopicID, Topic) VALUES (?,?)", (2, "Forces")),
    ("INSERT OR IGNORE INTO Topics(TopicID, Topic) VALUES (?,?)", (3, "Electricity")),
    ("INSERT OR IGNORE INTO Topics(TopicID, Topic) VALUES (?,?)", (4, "Magnetism and Electromagnetism")),
    ("INSERT OR IGNORE INTO Topics(TopicID, Topic) VALUES (?,?)", (5, "Waves")),
    ("INSERT OR IGNORE INTO Topics(TopicID, Topic) VALUES (?,?)", (6, "Energy")),
]

def init_db():
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DB() as db:
        for ddl in SCHEMA:
            db.conn.executescript(ddl)
        db.q("SELECT COUNT(*) FROM SchemaVersion")
        if db.one()[0] == 0:
            db.q("INSERT INTO SchemaVersion(Version) VALUES (1)")
        for q, params in SEED:
            try:
                db.q(q, params)
            except Exception:
                pass
        for u, rid in (("teacher",1), ("student",2)):
            db.q("SELECT 1 FROM UserDetails WHERE Username=?", (u,))
            if not db.one():
                db.q("INSERT INTO UserDetails(Username, Password, UserTypeID, TotalScore) VALUES (?,?,?,0)",
                      (u, _hash_pw("password123"), rid))
