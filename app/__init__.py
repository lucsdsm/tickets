import os 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# carrega variáveis de ambiente do arquivo .env
load_dotenv()

# inicializa extensões
db = SQLAlchemy() # para ORM
migrate = Migrate() # para migrações de banco de dados
bcrypt = Bcrypt() # para hashing de senhas

login_manager = LoginManager() # para gerenciamento de sessões de usuário
login_manager.login_view = 'auth.login' # rota de login
login_manager.login_message = 'Por favor, faça login para acessar esta página.' # mensagem de login
login_manager.login_message_category = 'info' # categoria da mensagem de login

# cria a aplicação Flask
def create_app():

    app = Flask(__name__)

    # configurações da aplicação com a url do banco de dados
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'minha_chave_secreta')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # inicializa as extensões com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    with app.app_context():

        # importa os modelos para que o SQLAlchemy possa reconhecê-los
        from .models import User # importa o modelo User para o login_manager

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # importa e registra os blueprints
        from .routes import main
        app.register_blueprint(main.main)

        from .routes import auth
        app.register_blueprint(auth.auth)

        # registra os comandos personalizados
        from . import commands
        app.cli.add_command(commands.create_admin)

        return app