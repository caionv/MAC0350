from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

curtidas = 0
aba_atual = "curtidas"

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

@app.get("/aba/curtidas", response_class=HTMLResponse)
async def get_curtidas(request: Request):
    global aba_atual
    aba_atual = "curtidas"
    return templates.TemplateResponse(request, "curtidas.html", {"curtidas": curtidas})

@app.get("/aba/jupiter", response_class=HTMLResponse)
async def get_jupiter(request: Request):
    global aba_atual
    aba_atual = "jupiter"
    return templates.TemplateResponse(request, "jupiter.html", {})

@app.get("/aba/professor", response_class=HTMLResponse)
async def get_professor(request: Request):
    global aba_atual
    aba_atual = "professor"
    return templates.TemplateResponse(request, "professor.html", {})

@app.post("/curtir", response_class=HTMLResponse)
async def curtir():
    global curtidas
    curtidas += 1
    return str(curtidas)

@app.delete("/curtir", response_class=HTMLResponse)
async def zerar_curtidas():
    global curtidas
    curtidas = 0
    return str(curtidas)

@app.get("/proxima-aba", response_class=HTMLResponse)
async def proxima_aba(request: Request):
    global aba_atual
    abas = ["curtidas", "jupiter", "professor"]
    idx = abas.index(aba_atual)
    prox_idx = (idx + 1) % len(abas)
    aba_atual = abas[prox_idx]
    
    if aba_atual == "curtidas":
        return templates.TemplateResponse(request, "curtidas.html", {"curtidas": curtidas})
    elif aba_atual == "jupiter":
        return templates.TemplateResponse(request, "jupiter.html", {})
    else:
        return templates.TemplateResponse(request, "professor.html", {})
