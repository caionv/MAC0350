from fastapi import FastAPI, Request, Form, Response, Depends, HTTPException, status, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Usuario(BaseModel):
    nome: str
    senha: str
    bio: str

usuarios_db = []

@app.get("/")
def get_cadastro(request: Request):
    return templates.TemplateResponse(request=request, name="cadastro.html")

@app.post("/users")
def criar_usuario(user: Usuario):
    usuarios_db.append(user.model_dump())
    return {"mensagem": "Usuário criado"}

@app.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
def post_login(response: Response, nome: str = Form(...), senha: str = Form(...)):
    usuario_encontrado = None
    for u in usuarios_db:
        if u["nome"] == nome and u["senha"] == senha:
            usuario_encontrado = u
            break
    
    if not usuario_encontrado:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    response = RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="session_user", value=nome)
    return response

def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    if not session_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não logado")
    
    user = next((u for u in usuarios_db if u["nome"] == session_user), None)
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    return user

@app.get("/home")
def get_home(request: Request, user: dict = Depends(get_active_user)):
    return templates.TemplateResponse(request=request, name="perfil.html", context={"user": user})
