from app import db
from flask_bcrypt import Bcrypt # para hashing de senhas
from flask_login import UserMixin # para integração com Flask-Login
from datetime import datetime

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
    
    # Relações
    sectors = db.relationship('Sector', secondary=user_sectors, back_populates='users')
    created_tickets = db.relationship('Ticket', foreign_keys='Ticket.creator_id', back_populates='creator', lazy='dynamic')
    assigned_tickets = db.relationship('Ticket', foreign_keys='Ticket.assignee_id', back_populates='assignee', lazy='dynamic')

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
    
    # Relações
    users = db.relationship('User', secondary=user_sectors, back_populates='sectors')
    subjects = db.relationship('Subject', secondary=subject_sectors, back_populates='sectors')
    tickets = db.relationship('Ticket', foreign_keys='Ticket.sector_id', back_populates='sector', lazy='dynamic')

    def __repr__(self):
        return f'<Sector {self.name}>'
    
class Subject(db.Model):
    """Modelo de dados para o assunto."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relações
    sectors = db.relationship('Sector', secondary=subject_sectors, back_populates='subjects')
    tickets = db.relationship('Ticket', foreign_keys='Ticket.subject_id', back_populates='subject', lazy='dynamic')

    def __repr__(self):
        return f'<Subject {self.name}>'

class Status(db.Model):
    """Modelo de dados para o status."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    symbol = db.Column(db.String(10), nullable=False, default="●")

    # Relações
    tickets = db.relationship('Ticket', foreign_keys='Ticket.status_id', back_populates='status', lazy='dynamic')

    def __repr__(self):
        return f'<Status {self.name}>'

class Priority(db.Model):
    """Modelo de dados para a prioridade."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(7), nullable=False, default="#FFFFFF")

    # Relações
    tickets = db.relationship('Ticket', foreign_keys='Ticket.priority_id', back_populates='priority', lazy='dynamic')

    def __repr__(self):
        return f'<Priority {self.name}>'

class Ticket(db.Model):
    """Modelo de dados para o ticket."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    assigned_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())
    closed_at = db.Column(db.DateTime, nullable=True)

    # Chaves estrangeiras
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    sector_id = db.Column(db.Integer, db.ForeignKey('sector.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    priority_id = db.Column(db.Integer, db.ForeignKey('priority.id'), nullable=False)

    # Relações
    creator = db.relationship('User', foreign_keys=[creator_id], back_populates='created_tickets')
    assignee = db.relationship('User', foreign_keys=[assignee_id], back_populates='assigned_tickets')
    sector = db.relationship('Sector', foreign_keys=[sector_id], back_populates='tickets')
    subject = db.relationship('Subject', foreign_keys=[subject_id], back_populates='tickets')
    status = db.relationship('Status', foreign_keys=[status_id], back_populates='tickets')
    priority = db.relationship('Priority', foreign_keys=[priority_id], back_populates='tickets')

    def __repr__(self):
        return f'<Ticket {self.title}>'
    
class TicketMessage(db.Model):
    """Modelo de dados para as mensagens dos tickets."""
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    # Chaves estrangeiras
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relações
    ticket = db.relationship('Ticket', foreign_keys=[ticket_id], backref=db.backref('messages', lazy='dynamic'))
    author = db.relationship('User', foreign_keys=[author_id])

    def __repr__(self):
        return f'<TicketMessage {self.id}>'