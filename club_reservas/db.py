from sqlalchemy import create_engine


DATABASE_URL = (
    "mysql+mysqlconnector://usuario:contraseña"
    "@127.0.0.1:3306/club_reservas"
)

engine = create_engine(DATABASE_URL)