
from .dal.db import init_db
from .migrate import run as run_migrations
from .ui.login import show as show_login
from .ui.menu import show_home

def main():
    init_db()
    run_migrations()
    def after_login(user_id, role, full_name):
        show_home(user_id, role, full_name)
    show_login(after_login)

if __name__ == "__main__":
    main()
