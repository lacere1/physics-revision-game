# GCSE Physics Revision Game


A desktop learning app that helps students revise with **adaptive quizzes**, **instant feedback**, and **lightweight analytics**.


---

## 🚀 Quick Start (SQLite — default)

```bash
python -m pip install -r requirements.txt
python launch.py
```
Logins: `teacher/password123` · `student/password123`

> Data lives in your user profile (e.g., `%AppData%\RevisionGame\ProgramDatabase.sqlite3`).

---

## Features

- **Adaptive practice** — prioritizes questions you’ve missed more often
- **Explanations** — every answer shows “why this is right”
- **Progress & leaderboard** — per-topic accuracy, CSV export for teachers
- **Security** — bcrypt password hashing, parameterized SQL, least‑privilege roles
- **UX polish** — keyboard navigation (Enter to submit), non‑blocking feedback, focus states
- **Accessibility** — high‑contrast theme and larger font option

---

## 🛠 Tech Stack

- **Python 3.10+**, **Tkinter**
- **SQLite** (default) or **MySQL** (optional)
- **bcrypt**
- Thin **DAL** (parameterized queries)
- Lightweight **migrations** (version table + SQL files)

---

## 🧭 Architecture

```
revision_game/
  app.py                 # bootstrap DB+migrations, launch UI
  ui/                    # views (login, menu, quiz, reports)
  core/                  # services (auth, topics, scoring)
  dal/                   # DB wrapper (SQLite/MySQL), migrations, seed
  assets/                # question banks (JSON)
  tests/                 # unit tests (services + DAL)
```

---