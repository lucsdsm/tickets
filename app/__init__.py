import os 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt

# carrega variáveis de ambiente do arquivo .env
load_dotenv()

# inicializa extensões
db = SQLAlchemy() # para ORM
migrate = Migrate() # para migrações de banco de dados
bcrypt = Bcrypt() # para hashing de senhas

# cria a aplicação Flask
def create_app():

    app = Flask(__name__)

    # configurações da aplicação com a url do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # inicializa as extensões com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    with app.app_context():

        # importa os modelos para que o SQLAlchemy possa reconhecê-los
        from . import models

        # importa e registra os blueprints
        from . import main
        app.register_blueprint(main.main)

        # registra os comandos personalizados
        from . import commands
        app.cli.add_command(commands.create_admin)

        return app