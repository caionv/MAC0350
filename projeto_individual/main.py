from fastapi import FastAPI, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import os
import jwt
from datetime import datetime, timedelta

from database import (
    create_db_and_tables,
    initialize_members,
    get_session,
    Member,
    Ata,
    Feedback,
    pwd_context
)

SECRET_KEY = "minhasenha"
ALGORITHM = "HS256"

def get_current_user(request: Request, session: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        token = token.replace("Bearer ", "")
        email = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
        return session.exec(select(Member).where(Member.email == email)).first()
    except:
        return None

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

@app.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    user = get_current_user(request, next(get_session()))
    return templates.TemplateResponse(request=request, name="login.html", context={"user": user})

@app.post("/login", response_class=HTMLResponse)
def login(
    response: Response, 
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    user = session.exec(select(Member).where(Member.email == username)).first()
    if not user or not pwd_context.verify(password, user.password):
        return "Login incorreto"
    
    exp = datetime.utcnow() + timedelta(minutes=60)
    token = jwt.encode({"sub": user.email, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)
    
    response = HTMLResponse("OK")
    response.headers["HX-Redirect"] = "/"
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response

@app.post("/logout", response_class=HTMLResponse)
def logout(response: Response):
    response = HTMLResponse("OK")
    response.headers["HX-Redirect"] = "/"
    response.delete_cookie("access_token")
    return response

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, session: Session = Depends(get_session)):
    user = get_current_user(request, session)
    members = session.exec(select(Member)).all()
    return templates.TemplateResponse(request=request, name="index.html", context={
        "request": request, 
        "members": members,
        "user": user
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

@app.get("/feedbacks", response_class=HTMLResponse)
def read_feedbacks(request: Request, session: Session = Depends(get_session)):
    user = get_current_user(request, session)
    if not user: return "Acesso negado"

    feedbacks_list = session.exec(select(Feedback).order_by(Feedback.id.desc())).all()
    return templates.TemplateResponse(request=request, name="feedbacks.html", context={
        "request": request, 
        "feedbacks": feedbacks_list,
        "user": user
    })

@app.get("/atas", response_class=HTMLResponse)
def read_atas(request: Request, session: Session = Depends(get_session)):
    user = get_current_user(request, session)
    atas = session.exec(select(Ata).order_by(Ata.id.desc())).all()
    members = session.exec(select(Member)).all()
    return templates.TemplateResponse(request=request, name="atas.html", context={
        "request": request, 
        "atas": atas,
        "members": members,
        "user": user
    })

@app.post("/atas", response_class=HTMLResponse)
def create_ata(
    request: Request,
    title: str = Form(...),
    date: str = Form(...),
    content: str = Form(...),
    author_id: int = Form(...),
    session: Session = Depends(get_session),
    user: Member = Depends(get_current_user)
):
    if not user: return "Acesso negado"

    ata = Ata(title=title, date=date, content=content, author_id=author_id)
    session.add(ata)
    session.commit()
    session.refresh(ata)
    
    return templates.TemplateResponse(request=request, name="components/ata_item.html", context={
        "request": request,
        "ata": ata,
        "user": user
    })

@app.get("/atas/search", response_class=HTMLResponse)
def search_atas(
    request: Request,
    q: str = "",
    session: Session = Depends(get_session)
):
    user = get_current_user(request, session)
    query = select(Ata)
    if q:
        query = query.where((Ata.title.contains(q)) | (Ata.date.contains(q)))
    atas = session.exec(query.order_by(Ata.id.desc())).all()
    
    return templates.TemplateResponse(request=request, name="components/ata_list.html", context={
        "request": request,
        "atas": atas,
        "user": user
    })

@app.get("/atas/{id}/edit", response_class=HTMLResponse)
def get_edit_ata(request: Request, id: int, session: Session = Depends(get_session)):
    user = get_current_user(request, session)
    if not user: return "Acesso negado"

    ata = session.get(Ata, id)
    members = session.exec(select(Member)).all()
    return templates.TemplateResponse(request=request, name="components/ata_edit.html", context={
        "request": request,
        "ata": ata,
        "members": members,
        "user": user
    })

@app.put("/atas/{id}", response_class=HTMLResponse)
def update_ata(
    request: Request,
    id: int,
    title: str = Form(...),
    date: str = Form(...),
    content: str = Form(...),
    author_id: int = Form(...),
    session: Session = Depends(get_session),
    user: Member = Depends(get_current_user)
):
    if not user: return "Acesso negado"

    ata = session.get(Ata, id)
    if not ata: return "Erro"
        
    ata.title = title
    ata.date = date
    ata.content = content
    ata.author_id = author_id
    session.add(ata)
    session.commit()
    session.refresh(ata)
    return templates.TemplateResponse(request=request, name="components/ata_item.html", context={
        "request": request,
        "ata": ata,
        "user": user
    })

@app.delete("/atas/{id}", response_class=HTMLResponse)
def delete_ata(id: int, session: Session = Depends(get_session), user: Member = Depends(get_current_user)):
    if not user: return "Acesso negado"

    ata = session.get(Ata, id)
    if ata:
        session.delete(ata)
        session.commit()
    return HTMLResponse("")
