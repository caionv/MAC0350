from sqlmodel import Field, SQLModel, create_engine, Session, Relationship
from typing import List, Optional
from datetime import datetime

class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    email: str
    
    atas: List["MeetingMinute"] = Relationship(back_populates="author")

class MeetingMinute(SQLModel, table=True):
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
        # Pega o primeiro para checar se a tabela está vazia
        # Nota: sqlmodel recomenda usar `session.exec(select(Member)).first()` mas esse jeito mais simples também funciona.
        from sqlmodel import select
        has_member = session.exec(select(Member)).first()
        if not has_member:
            members = [
                Member(name="Alice Ferreira", role="Presidenta", email="alice.bcc@ime.usp.br"),
                Member(name="Beto Carvalho", role="Vice-Presidente", email="beto.bcc@ime.usp.br"),
                Member(name="Cecília Santos", role="Diretora de Comunicação", email="cecilia.bcc@ime.usp.br")
            ]
            session.add_all(members)
            session.commit()

def get_session():
    with Session(engine) as session:
        yield session
