
from tkinter import *
from tkinter import messagebox
from ..core.auth_service import verify_user

def show(on_success):
    root = Tk()
    root.title("Revision Game — Login")
    root.geometry("420x220+350+200")

    Label(root, text="Username").pack(pady=(16,4))
    u = Entry(root, width=28); u.pack()
    Label(root, text="Password").pack(pady=(8,4))
    p = Entry(root, width=28, show="*"); p.pack()

    status = Label(root, text="", fg="red"); status.pack(pady=8)
    submitting = {"flag": False}

    def submit():
        if submitting["flag"]:
            return
        username_val = (u.get() or "").strip().lower()
        password_val = p.get() or ""
        res = verify_user(username_val, password_val)
        if res:
            submitting["flag"] = True
            uid, role = res
            root.destroy()
            full_name = username_val or "User"
            on_success(uid, role, full_name)
        else:
            status.config(text="Invalid credentials")

    Button(root, text="Sign in", command=submit).pack(pady=8)
    root.bind("<Return>", lambda e: submit())
    root.mainloop()
