# To-Do List API  

## Descrição

Este projeto é uma API para gerenciamento de tarefas (To-Do List) construída com Flask. A API permite que os usuários adicionem, atualizem, removam e listem tarefas. O projeto utiliza MySQL para armazenamento persistente, Redis para cache e autenticação com JSON Web Tokens (JWT) para garantir a segurança das operações.

### Funcionalidades

- Adicionar uma nova tarefa.
- Atualizar o status de uma tarefa (pendente/completa).
- Remover uma tarefa.
- Listar todas as tarefas.
- Autenticação de usuário com JWT para acesso seguro às rotas.
- Utilização de Redis para cache de sessões ou tarefas temporárias.

### Tecnologias Utilizadas

- Backend: Flask, Flask-JWT-Extended, SQLAlchemy
- Banco de Dados: MySQL
- Cache: Redis
- Autenticação: JWT
- Frontend: HTML, CSS e JavaScript (AJAX) para comunicação com a API

## Configuração e Execução Local
Pré-requisitos

- Python 3
- MySQL
- Redis
- bibliotecas em requirements.txt

1. Clonar o Repositório

2. Instalar Dependências

Crie um ambiente virtual (opcional) e instale as dependências:
    
```bash	
# Criar ambiente virtual
python -m venv venv
# Ativar o ambiente virtual (Windows)
.\venv\Scripts\activate
# Ativar o ambiente virtual (Mac/Linux)
source venv/bin/activate

# Instalar as dependências
pip install -r requirements.txt
```

3. Configurar o Banco de Dados MySQL

Certifique-se de que o MySQL está rodando.

No MySQL, crie um banco de dados:

```sql
CREATE DATABASE todo_db;
```

Atualize as variáveis de configuração de banco de dados no código (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME) com as credenciais do seu MySQL.

4. Configurar o Redis

    Certifique-se de que o Redis está rodando localmente (geralmente, a porta padrão é 6379).

5. Executar a Aplicação

Crie as tabelas no banco de dados:

```bash
python main.py
```

6. Use a API localmente em http://127.0.0.1:5000/

Para usar a interface de usuário, abra o arquivo `index.html` com o navegador.

## Endpoints Principais

Método	Endpoint	Descrição
POST	/login	Autenticar e obter o token JWT.
GET	/tasks	Listar todas as tarefas.
POST	/tasks	Adicionar nova tarefa.
PUT	/tasks/<task_id>	Atualizar uma tarefa existente.
DELETE	/tasks/<task_id>	Remover uma tarefa.