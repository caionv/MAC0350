# Representação Discente BCC IME USP 2026

## Sobre o Projeto
Este web app foi desenvolvido como projeto individual para a disciplina **MAC0350 - Introdução ao Desenvolvimento de Sistemas de Software**. O objetivo é servir como a plataforma oficial da Representação Discente do Bacharelado em Ciência da Computação do IME-USP de 2026. 

O sistema facilita a transparência e a comunicação, oferecendo informações sobre a chapa, um histórico de atas de reuniões e um canal direto para os alunos enviarem feedbacks e requisições.

## Funcionalidades
* **Páginas Informativas:** Contato de todos os membros e resumo das pautas gerais da chapa.
* **Mural de Atas (Blog):** Feed atualizado com os registros das últimas reuniões.
* **Caixa de Feedbacks:** Formulário para os alunos enviarem pedidos, dúvidas ou sugestões para a representação.
* **Busca dos objetos** Busca rápida de atas por título/data.

## Tecnologias Utilizadas
Este projeto foi construído seguindo as especificações da disciplina:

* **Front-end:** HTML, CSS e JavaScript. O layout é responsivo, garantindo boa usabilidade tanto em dispositivos móveis quanto em PCs. Foram desenvolvidas múltiplas telas (Home/Pautas, Mural de Atas e Contato/Feedback).
* **Back-end:** Construído utilizando o framework **FastAPI**.
* **Banco de Dados (SQL):** Modelagem com relacionamentos para estruturar os dados do sistema.
  * **Modelos Principais:** `Membro`, `Ata` e `Feedback`.
  * **Relacionamentos:** Relação *One to Many* entre `Membro` e `Ata`, onde um membro é o autor responsável por publicar uma ata.
* **HTMX (Operações CRUD):**
  * `hx-post`: Utilizado para o envio de novos formulários de feedback e criação de novas atas.
  * `hx-get`: Utilizado para buscar a lista de atas cadastradas e exibi-las na tela.
  * `hx-put`: Utilizado para editar e atualizar o texto de uma ata já publicada.
  * `hx-delete`: Utilizado para excluir uma ata ou arquivar um feedback.

##
  **Autor:** Caio Nicoluzzi Vieira
  
  **NUSP:**  14562960
