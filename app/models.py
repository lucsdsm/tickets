from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    access_level = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f'<User {self.username}>'