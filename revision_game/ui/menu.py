
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from ..core.score_service import leaderboard, user_history
from ..core.topic_service import topics
from ..core.auth_service import create_user, change_password
from ..quiz_engine import load_questions, prioritize_for_user, record_result
from ..dal.db import DB
import csv
FONT_H = ("Segoe UI", 14, "bold"); FONT_N = ("Segoe UI", 11)
def _center(win, w=900, h=600):
    try: win.geometry(f"{w}x{h}+200+120")
    except Exception: pass
def _make_window(title):
    win = Toplevel(); win.title(f"{title}"); _center(win, 800, 520); return win
def show_home(user_id: int, role: str, full_name: str):
    home = Tk(); home.title(f"Revision Game — Home"); _center(home, 900, 600)
    Label(home, text=f"Welcome {full_name} ({role})", font=FONT_H).pack(pady=10)
    btns = Frame(home); btns.pack(pady=8)
    def add_btn(text, cmd): b = Button(btns, text=text, width=24, command=cmd); b.pack(pady=6); return b
    add_btn("Start Quiz", lambda: show_quiz(user_id, role))
    add_btn("My Progress", lambda: show_history(user_id))
    add_btn("Leaderboard", show_leaderboard)
    if (role or "").strip().lower() == "teacher":
        Label(home, text="Teacher tools", font=FONT_H).pack(pady=(18,4))
        add_btn("Create User", show_create_user); add_btn("Change Password", show_change_password)
        add_btn("Export Scores (CSV)", export_scores_csv); add_btn("List All Users", list_all_users)
    Button(home, text="Close", command=home.destroy).pack(pady=16); home.mainloop()
def show_quiz(user_id: int, role: str):
    win = _make_window("Start Quiz"); Label(win, text="Choose a topic", font=FONT_H).pack(pady=6)
    lb = Listbox(win, height=8, width=50, font=FONT_N); lb.pack(pady=6)
    tps = topics(); 
    for tid, name in tps: lb.insert(END, f"{tid}. {name}")
    mode = BooleanVar(value=True); Checkbutton(win, text="Timed mode (30s/question)", variable=mode).pack(pady=4)
    def begin():
        if not lb.curselection(): messagebox.showinfo("Pick a topic", "Please select a topic first."); return
        idx = lb.curselection()[0]; topic_id, topic_name = tps[idx]
        _run_quiz(win, user_id, topic_id, topic_name, timed=mode.get())
    Button(win, text="Start", command=begin).pack(pady=8)
def _load_bank(topic_id: int):
    name_map = {1:"particles_quiz",2:"forces_quiz",3:"electricity_quiz",4:"magnetism_quiz",5:"waves_quiz",6:"energy_quiz"}
    file_name = name_map.get(topic_id, "particles_quiz"); assets_dir = Path(__file__).resolve().parents[1] / "assets"
    return load_questions(assets_dir, file_name, topic_id)
def _run_quiz(parent, user_id: int, topic_id: int, topic_name: str, timed: bool):
    qs = _load_bank(topic_id); qs = prioritize_for_user(user_id, topic_id, qs)
    if not qs: messagebox.showinfo("No questions", "No items found for this topic."); return
    qwin = _make_window(f"Quiz — {topic_name}"); state = {'i':0,'score':0,'timed':timed,'time_left':30,'tick_id':None}
    qlbl = Label(qwin, text="", font=FONT_H, wraplength=760, justify=LEFT); qlbl.pack(pady=(10,6))
    opt_var = IntVar(value=-1); radios=[]; 
    for i in range(4):
        rb = Radiobutton(qwin, text="", font=FONT_N, variable=opt_var, value=i+1, anchor="w", justify=LEFT); rb.pack(fill='x', padx=16, pady=4); radios.append(rb)
    expl = Label(qwin, text="", font=FONT_N, fg="white", bg="gray25", wraplength=760, justify=LEFT); expl.pack(fill='x', padx=10, pady=8)
    timer_lbl = Label(qwin, text="", font=FONT_N); timer_lbl.pack()
    def cancel_timer():
        tid = state.get('tick_id')
        if tid is not None:
            try: qwin.after_cancel(tid)
            except Exception: pass
            state['tick_id'] = None
    def schedule_tick(): state['tick_id'] = qwin.after(1000, _tick)
    def render():
        cancel_timer(); i = state['i']; q = qs[i]
        qlbl.config(text=f"Q{i+1}. {q['question']}")
        for j, rb in enumerate(radios):
            if j < len(q['options']): rb.config(text=f"{j+1}. {q['options'][j]}"); rb.configure(state=NORMAL)
            else: rb.config(text=f"{j+1}."); rb.configure(state=DISABLED)
        opt_var.set(-1); expl.config(text=""); timer_lbl.config(text="")
        if state['timed']: state['time_left'] = 30; timer_lbl.config(text=f"Time: {state['time_left']}s"); schedule_tick()
    def _tick():
        if not state['timed'] or state['i'] >= len(qs): cancel_timer(); return
        state['time_left'] -= 1
        if state['time_left'] <= 0: cancel_timer(); submit(timeout=True); return
        timer_lbl.config(text=f"Time: {state['time_left']}s"); schedule_tick()
    def submit(timeout=False):
        cancel_timer(); i = state['i']; q = qs[i]; sel = opt_var.get(); correct = (sel == q['answer']) and not timeout
        record_result(user_id, topic_id, q['qhash'], bool(correct))
        if correct: state['score'] += 1; expl.config(text=f"Correct ✓  {q.get('explanation','')}", bg='darkgreen')
        else: expl.config(text=f"Incorrect ✗  {q.get('explanation','')}", bg='darkred')
        for rb in radios: rb.configure(state=DISABLED)
        qwin.after(900, next_q)
    def next_q():
        state['i'] += 1
        if state['i'] >= len(qs): finish()
        else: render()
    def finish():
        cancel_timer(); total = len(qs); score = state['score']; from ..core.score_service import add_score; add_score(user_id, topic_id, score)
        messagebox.showinfo("Done", f"You scored {score} / {total}"); qwin.destroy()
    def on_close(): cancel_timer(); qwin.destroy()
    qwin.protocol("WM_DELETE_WINDOW", on_close)
    Button(qwin, text='Submit', command=lambda: submit(False)).pack(pady=8); render()
def show_leaderboard():
    win = _make_window("Leaderboard"); Label(win, text="Top Students", font=FONT_H).pack(pady=6)
    tree = ttk.Treeview(win, columns=('user','score'), show='headings', height=12); tree.heading('user', text='Username'); tree.heading('score', text='Total Score')
    tree.pack(fill='both', expand=True, padx=10, pady=10)
    for u, s in leaderboard(limit=25): tree.insert('', END, values=(u, s))
def show_history(user_id: int):
    win = _make_window("My Progress"); Label(win, text="Your Recent Scores", font=FONT_H).pack(pady=6)
    tree = ttk.Treeview(win, columns=('topic','score','date'), show='headings', height=12)
    for c,t in [('topic','Topic'),('score','Score'),('date','Date')]: tree.heading(c, text=t)
    tree.pack(fill='both', expand=True, padx=10, pady=10)
    for topic, score, date in user_history(user_id): tree.insert('', END, values=(topic, score, date))
def show_create_user():
    win = _make_window("Create User"); Label(win, text="Create User", font=FONT_H).pack(pady=8)
    f = Frame(win); f.pack(pady=8); Label(f, text="Username").grid(row=0, column=0, sticky="e", padx=6, pady=6)
    euser = Entry(f, width=28); euser.grid(row=0, column=1, padx=6, pady=6)
    Label(f, text="Password").grid(row=1, column=0, sticky="e", padx=6, pady=6); epw = Entry(f, width=28, show='*'); epw.grid(row=1, column=1, padx=6, pady=6)
    role = StringVar(value='Student'); ttk.Combobox(f, textvariable=role, values=['Teacher','Student'], state='readonly', width=25).grid(row=2, column=1, padx=6, pady=6)
    msg = Label(win, text='', fg='red'); msg.pack()
    def do_create():
        u = (euser.get() or '').lower().strip(); p = epw.get() or ''; rid = 1 if role.get()=='Teacher' else 2
        try: create_user(u, p, rid); msg.config(text='User created ✓', fg='green')
        except Exception as e: msg.config(text=f'Error: {e}', fg='red')
    Button(win, text='Create', command=do_create).pack(pady=10)
def show_change_password():
    win = _make_window("Change Password"); Label(win, text="Change Password", font=FONT_H).pack(pady=8)
    f = Frame(win); f.pack(pady=8); Label(f, text="Username").grid(row=0, column=0, sticky="e", padx=6, pady=6)
    euser = Entry(f, width=28); euser.grid(row=0, column=1, padx=6, pady=6)
    Label(f, text="New Password").grid(row=1, column=0, sticky="e", padx=6, pady=6); epw = Entry(f, width=28, show='*'); epw.grid(row=1, column=1, padx=6, pady=6)
    msg = Label(win, text='', fg='red'); msg.pack()
    def do_change():
        u = (euser.get() or '').lower().strip(); p = epw.get() or ''
        with DB() as db: db.q('SELECT UserID FROM UserDetails WHERE Username=?', (u,)); row = db.one()
        if not row: msg.config(text='No such user', fg='red'); return
        try: change_password(row[0], p); msg.config(text='Password changed ✓', fg='green')
        except Exception as e: msg.config(text=f'Error: {e}', fg='red')
    Button(win, text='Change', command=do_change).pack(pady=10)
def list_all_users():
    win = _make_window("All Users"); Label(win, text="Users", font=FONT_H).pack(pady=6)
    tree = ttk.Treeview(win, columns=('id','username','role','score'), show='headings', height=12)
    for c,h in [('id','ID'),('username','Username'),('role','Role'),('score','TotalScore')]: tree.heading(c, text=h)
    tree.pack(fill='both', expand=True, padx=10, pady=10)
    with DB() as db: db.q('''SELECT U.UserID, U.Username, T.UserType, U.TotalScore
                 FROM UserDetails U JOIN UserTypes T ON T.UserTypeID=U.UserTypeID
                 ORDER BY U.UserID'''); rows = db.all()
    for uid, uname, r, score in rows: tree.insert('', END, values=(uid, uname, r, score))
def export_scores_csv():
    path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')], initialfile='scores.csv')
    if not path: return
    with DB() as db: db.q('''SELECT U.Username, T.Topic, G.Score, G.Date
                 FROM GameScores G
                 JOIN UserDetails U ON U.UserID=G.UserID
                 JOIN Topics T ON T.TopicID=G.TopicID
                 ORDER BY G.Date DESC'''); rows = db.all()
    try:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f); w.writerow(['Username','Topic','Score','Date']); w.writerows(rows)
        messagebox.showinfo('Export', f'Saved to {path}')
    except Exception as e:
        messagebox.showerror('Export', f'Failed: {e}')
