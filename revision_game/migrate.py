
from .dal.db import DB
def run():
    with DB() as db:
        db.q("CREATE TABLE IF NOT EXISTS SchemaVersion(Version INTEGER NOT NULL)")
        db.q("SELECT COALESCE(MAX(Version), 1) FROM SchemaVersion")
        row = db.one()
        if not row or row[0] is None:
            db.q("INSERT INTO SchemaVersion(Version) VALUES (1)")
