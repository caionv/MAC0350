def buscar_alunos(busca):
    with Session(engine) as session:
        query = select(Aluno).where(col(Aluno.nome).contains(busca)).order_by(Aluno.nome)
        return session.exec(query).all()
    
@app.get("/lista", response_class=HTMLResponse)
def lista(request: Request, busca: str | None = '', pagina: int = 1):
    todos_alunos = buscar_alunos(busca)
    
    itens_por_pagina = 5
    inicio = (pagina - 1) * itens_por_pagina
    fim = inicio + itens_por_pagina
    
    alunos_paginados = todos_alunos[inicio:fim]
    
    total_paginas = (len(todos_alunos) + itens_por_pagina - 1) // itens_por_pagina
    if total_paginas == 0:
        total_paginas = 1

    return templates.TemplateResponse(request, "lista.html", {
        "alunos": alunos_paginados,
        "busca": busca,
        "pagina": pagina,
        "total_paginas": total_paginas
    })
