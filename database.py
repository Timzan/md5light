import sqlalchemy
from databases import Database

DATABASE_URL = "sqlite:///md5.db"
database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

checksums = sqlalchemy.Table(
    "checksums",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("url", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String),
    sqlalchemy.Column("status_id", sqlalchemy.String),
    sqlalchemy.Column("checksum", sqlalchemy.String),
    sqlalchemy.Column("status", sqlalchemy.String)
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

