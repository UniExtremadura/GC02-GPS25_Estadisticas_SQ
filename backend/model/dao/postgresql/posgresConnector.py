from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

class PostgreSQLConnector:
    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/estadisticas")
        self.engine = create_engine(self.DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()
