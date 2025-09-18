
import os, sys
from pathlib import Path

def _user_data_dir(app="RevisionGame"):
    if sys.platform.startswith("win"):
        base = os.getenv("APPDATA") or os.path.expanduser("~")
        return Path(base)/app
    elif sys.platform == "darwin":
        return Path.home()/ "Library" / "Application Support" / app
    else:
        return Path(os.getenv("XDG_DATA_HOME", Path.home()/".local/share"))/app

DATA_DIR = _user_data_dir()
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "ProgramDatabase.sqlite3"
