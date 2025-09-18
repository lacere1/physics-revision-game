
from ..dal.db import DB, bcrypt, _hash_pw

def verify_user(username: str, input_password: str):
    with DB() as db:
        db.q("""            SELECT UserDetails.UserID, UserTypes.UserType, UserDetails.Password
            FROM UserDetails
            JOIN UserTypes ON UserTypes.UserTypeID = UserDetails.UserTypeID
            WHERE Username = ?
        """, (username,))
        row = db.one()
    if not row:
        return None
    uid, role, pw = row
    ok = False
    if bcrypt and isinstance(pw, str) and pw.startswith("$2"):
        try:
            ok = bcrypt.checkpw(input_password.encode(), pw.encode())
        except Exception:
            ok = False
    else:
        ok = (input_password == pw)
    return (uid, role) if ok else None

def create_user(username: str, password: str, role_id: int):
    with DB() as db:
        db.q("INSERT INTO UserDetails(Username, Password, UserTypeID) VALUES (?,?,?)",
             (username, _hash_pw(password), role_id))

def change_password(user_id: int, new_password: str):
    with DB() as db:
        db.q("UPDATE UserDetails SET Password=? WHERE UserID=?",
             (_hash_pw(new_password), user_id))
