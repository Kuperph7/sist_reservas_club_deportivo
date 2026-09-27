import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine


DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "club_reservas")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


if not DB_USER or not DB_PASSWORD:
    raise RuntimeError(
        "Faltan DB_USER o DB_PASSWORD"
    )


DATABASE_URL = (
    f"mysql+mysqlconnector://"
    f"{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)