from app import db
from flask_bcrypt import Bcrypt # para hashing de senhas
from flask_login import UserMixin # para integração com Flask-Login

bcrypt = Bcrypt() # para hashing de senhas

# tabela de junção usuário-setor
user_sectors = db.Table('user_sectors',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('sector_id', db.Integer, db.ForeignKey('sector.id'), primary_key=True)
)

# tabela de junção assunto-setor
subject_sectors = db.Table('subject_sectors',
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True),
    db.Column('sector_id', db.Integer, db.ForeignKey('sector.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    """Modelo de dados para o usuário."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    
    sectors = db.relationship('Sector', secondary=user_sectors, back_populates='users')

    @property
    def is_admin(self) -> bool:
        """Verifica se o nível de acesso do usuário de administradora.

        Returns:
            bool: True se o usuário for um administrador, False caso contrário.
        """

        return self.admin == True
    
    # gera um hash a partir de uma senha e o armazena
    def set_password(self, password) -> None:
        """Gera um hash a partir da senha fornecida e o armazena no campo password_hash.

        Args:
            password (str): A senha a ser convertida em hash.
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # verifica se uma senha fornecida corresponde ao hash armazenado
    def check_password(self, password) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado.

        Args:
            password (str): A senha a ser verificada.
        
        Returns:
            bool: True se a senha corresponder ao hash, False caso contrário.
        """
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<User {self.username}>'
    
class Sector(db.Model):
    """Modelo de dados para o setor."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(7), nullable=False, default="#2C2C2C")
    
    users = db.relationship('User', secondary=user_sectors, back_populates='sectors')
    subjects = db.relationship('Subject', secondary=subject_sectors, back_populates='sectors')

    def __repr__(self):
        return f'<Sector {self.name}>'
    
class Subject(db.Model):
    """Modelo de dados para o assunto."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relação para aceder a `subject.sectors`
    sectors = db.relationship('Sector', secondary=subject_sectors, back_populates='subjects')

    def __repr__(self):
        return f'<Subject {self.name}>'

    

    
