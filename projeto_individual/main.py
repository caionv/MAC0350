from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import os

from database import (
    create_db_and_tables,
    initialize_members,
    get_session,
    Member,
    Ata,
    Feedback
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    initialize_members()
    yield

app = FastAPI(lifespan=lifespan)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

os.makedirs("templates/components", exist_ok=True)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, session: Session = Depends(get_session)):
    members = session.exec(select(Member)).all()
    return templates.TemplateResponse(request=request, name="index.html", context={
        "request": request, 
        "members": members
    })

@app.post("/feedback", response_class=HTMLResponse)
def create_feedback(
    request: Request,
    student_name: str = Form(default="Anônimo"),
    message: str = Form(...),
    session: Session = Depends(get_session)
):
    feedback = Feedback(student_name=student_name, message=message)
    session.add(feedback)
    session.commit()
    return HTMLResponse(
        "<div class='alert-success'>Dúvida/Sugestão enviada com sucesso! A representação técnica agradece.</div>"
    )

@app.get("/atas", response_class=HTMLResponse)
def read_atas(request: Request, session: Session = Depends(get_session)):
    atas = session.exec(select(Ata).order_by(Ata.id.desc())).all()
    members = session.exec(select(Member)).all()
    return templates.TemplateResponse(request=request, name="atas.html", context={
        "request": request, 
        "atas": atas,
        "members": members
    })

@app.post("/atas", response_class=HTMLResponse)
def create_ata(
    request: Request,
    title: str = Form(...),
    date: str = Form(...),
    content: str = Form(...),
    author_id: int = Form(...),
    session: Session = Depends(get_session)
):
    ata = Ata(title=title, date=date, content=content, author_id=author_id)
    session.add(ata)
    session.commit()
    session.refresh(ata)
    
    return templates.TemplateResponse(request=request, name="components/ata_item.html", context={
        "request": request,
        "ata": ata
    })

@app.get("/atas/search", response_class=HTMLResponse)
def search_atas(
    request: Request,
    q: str = "",
    session: Session = Depends(get_session)
):
    query = select(Ata)
    if q:
        query = query.where((Ata.title.contains(q)) | (Ata.date.contains(q)))
    atas = session.exec(query.order_by(Ata.id.desc())).all()
    
    return templates.TemplateResponse(request=request, name="components/ata_list.html", context={
        "request": request,
        "atas": atas
    })

@app.get("/atas/{id}/edit", response_class=HTMLResponse)
def get_edit_ata(request: Request, id: int, session: Session = Depends(get_session)):
    ata = session.get(Ata, id)
    members = session.exec(select(Member)).all()
    return templates.TemplateResponse(request=request, name="components/ata_edit.html", context={
        "request": request,
        "ata": ata,
        "members": members
    })

@app.put("/atas/{id}", response_class=HTMLResponse)
def update_ata(
    request: Request,
    id: int,
    title: str = Form(...),
    date: str = Form(...),
    content: str = Form(...),
    author_id: int = Form(...),
    session: Session = Depends(get_session)
):
    ata = session.get(Ata, id)
    if not ata:
        return HTMLResponse("Ata não encontrada", status_code=404)
        
    ata.title = title
    ata.date = date
    ata.content = content
    ata.author_id = author_id
    session.add(ata)
    session.commit()
    session.refresh(ata)
    return templates.TemplateResponse(request=request, name="components/ata_item.html", context={
        "request": request,
        "ata": ata
    })

@app.delete("/atas/{id}", response_class=HTMLResponse)
def delete_ata(id: int, session: Session = Depends(get_session)):
    ata = session.get(Ata, id)
    if ata:
        session.delete(ata)
        session.commit()
    return HTMLResponse("")
