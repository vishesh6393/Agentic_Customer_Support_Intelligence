from sqlmodel import Session, create_engine, text
from app.config import get_settings

engine = create_engine(get_settings().database_url, pool_pre_ping=True)


def get_session():
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    with Session(engine) as s:
        print(s.exec(text("select version()")).one()[0])