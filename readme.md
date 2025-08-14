> Em desenvolvimento 🚧 

# 🎫 tickets

Sistema de gerenciamento de tickets com autenticação local e via Google, desenvolvido em Flask.

## Funcionalidades (até o momento)

- Cadastro e login de usuários (local e Google OAuth)
- Dashboard personalizado para usuários autenticados
- Interface responsiva com Tailwind CSS e tema escuro/claro
- Migrações de banco de dados com Flask-Migrate/Alembic
- Integração com PostgreSQL via Docker Compose
- Scripts para criação de usuário admin via CLI

## Tecnologias utilizadas

- Python 3.11
- Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Bcrypt, Flask-Login
- Authlib (OAuth Google)
- Tailwind CSS (build automatizado via container Node)
- PostgreSQL (via Docker)
- Docker e Docker Compose

## Como rodar o projeto

1. **Clone o repositório e configure o arquivo `.env`** com as variáveis necessárias (exemplo: `FLASK_SECRET_KEY`, `DATABASE_URL`, `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`).

2. **Suba os containers:**
   ```sh
   docker-compose -f docker/docker-compose.yml up --build -d
   ```

3. **Acompanhe os logs:**
   ```sh
   docker-compose -f docker/docker-compose.yml logs -f web
   ```

4. **(Primeira vez) Inicialize as migrações:**
   ```sh
   docker-compose -f docker/docker-compose.yml exec web flask db init
   ```

5. **Crie as tabelas/migrações:**
   ```sh
   docker-compose -f docker/docker-compose.yml exec web flask db migrate -m "mensagem da migração"
   docker-compose -f docker/docker-compose.yml exec web flask db upgrade
   ```

6. **Crie um usuário admin para testes:**
   ```sh
   docker-compose -f docker/docker-compose.yml exec web flask create-admin
   ```

7. **Acesse a aplicação:**  
   http://localhost:5000

## Estrutura de pastas

- `app/` - Código fonte da aplicação Flask
  - `routes/` - Blueprints de rotas
  - `templates/` - Templates HTML (Jinja2)
  - `static/` - Arquivos estáticos (CSS gerado pelo Tailwind)
- `docker/` - Arquivos de configuração Docker/Docker Compose
- `migrations/` - Migrações do banco de dados Alembic
- `run.py` - Ponto de entrada da aplicação Flask

## Scripts úteis

Veja o arquivo [`comandos.txt`](comandos.txt) para exemplos de comandos Docker e Flask CLI.
