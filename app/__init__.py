import os 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix

# carrega variáveis de ambiente do arquivo .env
load_dotenv()

# inicializa extensões
db = SQLAlchemy() # para ORM
migrate = Migrate() # para migrações de banco de dados
bcrypt = Bcrypt() # para hashing de senhas
oauth = OAuth() # para autenticação OAuth

login_manager = LoginManager() # para gerenciamento de sessões de usuário
login_manager.login_view = 'auth.login' # rota de login
login_manager.login_message = 'Por favor, faça login para acessar esta página.' # mensagem de login
login_manager.login_message_category = 'info' # categoria da mensagem de login

# cria a aplicação Flask
def create_app() -> Flask:
    """Cria e configura a aplicação Flask."""

    app = Flask(__name__)

    # configura o aplicativo para usar o proxyfix (necessitei para acessar o app via smartphone através de tunel aqui do vscode)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    # configurações da aplicação com a url do banco de dados
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # inicializa as extensões com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    oauth.init_app(app)
    
    # configura o OAuth para o Google
    oauth.register(
        name='google',
        client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    with app.app_context():

        # importa os modelos para que o SQLAlchemy possa reconhecê-los
        from .models import User # importa o modelo User para o login_manager

        # registra o carregador de usuário para o login_manager
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # importa e registra os blueprints
        from .routes import main
        app.register_blueprint(main.main)

        from .routes.auth import auth
        app.register_blueprint(auth.auth, url_prefix='/auth')

        from .routes.profile import profile
        app.register_blueprint(profile.profile, url_prefix='/profile')

        from .routes.panel import panel
        app.register_blueprint(panel.panel, url_prefix='/panel')

        from .routes.panel.users import users
        app.register_blueprint(users.users, url_prefix='/users')

        from .routes.panel.sectors import sectors
        app.register_blueprint(sectors.sectors, url_prefix='/sector')

        # registra os comandos personalizados
        from . import commands
        app.cli.add_command(commands.create_admin)

        return app