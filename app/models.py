from app import db
from flask_bcrypt import Bcrypt # para hashing de senhas
from flask_login import UserMixin # para integração com Flask-Login

bcrypt = Bcrypt() # para hashing de senhas

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    admin = db.Column(db.Integer, nullable=False, default=0)

    # gera um hash a partir de uma senha e o armazena
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # verifica se uma senha fornecida corresponde ao hash armazenado
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'