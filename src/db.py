from pathlib import Path

from sqlalchemy import MetaData, Table

from constants import DB_DIR, DB_FILE


def db_init() -> None:
    db_dir_path = Path(DB_DIR)
    dib_file_path = Path(DB_FILE)
    if not Path.exists(db_dir_path):
        Path.mkdir(db_dir_path)
        Path.touch(dib_file_path)
