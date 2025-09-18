
from ..dal.db import DB
def topics():
    with DB() as db:
        db.q("SELECT TopicID, Topic FROM Topics ORDER BY TopicID")
        rows = db.all()
    return rows
