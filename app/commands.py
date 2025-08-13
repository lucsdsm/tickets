import click
from flask.cli import with_appcontext
from . import db
from .models import User

@click.command(name='create-admin')
@with_appcontext
def create_admin():
    """cria um usuário administrador para testes."""
    
    # verifica se o admin já existe
    if User.query.filter_by(username='admin').first():
        print("Usuário 'admin' já existe.")
        return
        
    # cria o novo usuário admin
    admin_user = User(
        username='admin',
        first_name='Admin',
        last_name='Master',
        password_hash='admin',
        email='admin@tickets.com',
        admin=1
    )
    
    # define a senha usando o método set_password
    admin_user.set_password('admin')
    
    # salva o usuário no banco de dados
    db.session.add(admin_user)
    db.session.commit()
    
    print("usuário 'admin' criado com sucesso.")