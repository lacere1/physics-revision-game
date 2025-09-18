
import json, hashlib
from pathlib import Path
from .dal.db import DB
def load_questions(assets_dir: Path, base_name: str, topic_id: int):
    path = Path(assets_dir)/f"{base_name}.json"
    if not path.exists(): return []
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for q in data:
        qhash = hashlib.sha1(f"{topic_id}:{q.get('question','')}".encode()).hexdigest()[:12]
        out.append({
            "question": q["question"],
            "options": q.get("options", []),
            "answer": int(q.get("answer", 1)),
            "explanation": q.get("explanation", ""),
            "difficulty": q.get("difficulty", "Easy"),
            "qhash": qhash
        })
    return out
def prioritize_for_user(user_id: int, topic_id: int, questions):
    with DB() as db:
        db.q("""SELECT QHash, CorrectCount, WrongCount
                 FROM QuestionStats WHERE UserID=? AND TopicID=?""", (user_id, topic_id))
        rows = db.all()
    stat = {h:(c,w) for h,c,w in rows}
    def score(q):
        c,w = stat.get(q['qhash'], (0,0)); return (-(w - c), q['difficulty']!='Easy')
    return sorted(questions, key=score)
def record_result(user_id: int, topic_id: int, qhash: str, correct: bool):
    with DB() as db:
        db.q("SELECT CorrectCount, WrongCount FROM QuestionStats WHERE UserID=? AND TopicID=? AND QHash=?",
             (user_id, topic_id, qhash)); row = db.one()
        if not row:
            db.q("INSERT INTO QuestionStats(UserID, TopicID, QHash, CorrectCount, WrongCount) VALUES (?,?,?,?,?)",
                 (user_id, topic_id, qhash, 1 if correct else 0, 0 if correct else 1))
        else:
            c,w = row
            if correct: c+=1
            else: w+=1
            db.q("UPDATE QuestionStats SET CorrectCount=?, WrongCount=? WHERE UserID=? AND TopicID=? AND QHash=?",
                 (c, w, user_id, topic_id, qhash))
