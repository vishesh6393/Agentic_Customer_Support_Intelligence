from sqlmodel import Session, SQLModel, create_engine, text
from app.config import get_settings

engine = create_engine(get_settings().database_url, pool_pre_ping=True)


def get_session():
    with Session(engine) as session:
        yield session
def create_tables():
    from app.support_api import models  # noqa: F401  registers the tables
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    with Session(engine) as s:
        print(s.exec(text("select version()")).one()[0])