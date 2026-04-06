from sqlmodel import Field, SQLModel, create_engine, Session, Relationship
from typing import List, Optional
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    email: str
    tg: str
    password: str
    
    atas: List["Ata"] = Relationship(back_populates="author")

class Ata(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    date: str
    author_id: Optional[int] = Field(default=None, foreign_key="member.id")
    
    author: Optional[Member] = Relationship(back_populates="atas")

class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_name: str
    message: str
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

sqlite_file_name = "webmac.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def initialize_members():
    with Session(engine) as session:
        from sqlmodel import select
        has_member = session.exec(select(Member)).first()
        if not has_member:
            hashed_pwd = pwd_context.hash("senha")
            members = [
                Member(name="Nicolas Caldas Borsari", role="RD MAC, RD CoC-BCC, RD CCEx", email="nicborsari@usp.br", tg="@ncbor", password=hashed_pwd),
                Member(name="Kaiky Henrique Ribeiro Cintra", role="RD Suplente MAC", email="kaikycintra@usp.br", tg="@kai_kiwi77", password=hashed_pwd),
                Member(name="Gustavo Costa Arakaki", role="RD CCSL", email="gustavo.arakaki@usp.br", tg="@Ar4kaki", password=hashed_pwd),
                Member(name="Thalia Angelo Gomes da Silva", role="RD Suplente CCEx", email="thaliasilva@usp.br", tg="@thaliadsilva", password=hashed_pwd),
                Member(name="Sophia Helena Gutruf", role="RD Suplente CoC-BCC", email="sophiagutruf@usp.br", tg="@sophgut", password=hashed_pwd)
            ]
            session.add_all(members)
            session.commit()

def get_session():
    with Session(engine) as session:
        yield session
