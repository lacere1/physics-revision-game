
from datetime import datetime
from ..dal.db import DB
def add_score(user_id: int, topic_id: int, score: int):
    today = datetime.now().date().isoformat()
    with DB() as db:
        db.q("INSERT INTO GameScores(UserID, TopicID, Score, Date) VALUES (?,?,?,?)",
             (user_id, topic_id, score, today))
        db.q("UPDATE UserDetails SET TotalScore = TotalScore + ? WHERE UserID = ?",
             (score, user_id))
def leaderboard(limit: int=10, order: str="DESC"):
    order = "DESC" if (order or "").upper() != "ASC" else "ASC"
    with DB() as db:
        db.q(f"SELECT Username, TotalScore FROM UserDetails WHERE UserTypeID=2 ORDER BY TotalScore {order} LIMIT ?", (limit,))
        rows = db.all()
    return rows
def user_history(user_id: int):
    with DB() as db:
        db.q("""SELECT Topic, Score, Date
                 FROM GameScores JOIN Topics USING(TopicID)
                 WHERE UserID=? ORDER BY Date DESC""", (user_id,))
        rows = db.all()
    return rows
