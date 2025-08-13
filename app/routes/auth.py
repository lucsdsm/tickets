from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db, bcrypt, oauth

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.home'))
    
    # verifica se o método da requisição é POST
    if request.method == 'POST':
        # obtém os dados do formulário de login
        username = request.form['username']
        password = request.form['password']
        
        # busca o usuário pelo nome de usuário
        user = User.query.filter_by(username=username).first()
        # verifica se o usuário existe e se a senha está correta
        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return render_template('dashboard.html')
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.home'))

@auth.route('/google/login')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth.route('/google/callback')
def google_callback():
    try:
        # obtém o token de acesso
        token = oauth.google.authorize_access_token()
        # usa o token para obter as informações do utilizador
        user_info = oauth.google.userinfo()
        email = user_info['email']
    except Exception as e:
        flash(f"Ocorreu um erro durante a autenticação com a Google: {e}", "danger")
        return redirect(url_for('auth.login'))

    # verifica se o usuário já existe no banco de dados
    user = User.query.filter_by(email=email).first()

    # se o usuário não existir, cria um novo usuário
    if user is None:
        username_base = email.split('@')[0]
        username = username_base
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{username_base}{counter}"
            counter += 1
        
        user = User(
            email=email,
            username=username
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Que bom vê-lo pela primeira vez, {user.username}. A sua conta foi criada com sucesso!", 'success')
        return render_template('dashboard.html')
    
    else:
        login_user(user)
        flash(f'Bem-vindo de volta, {user.username}!', 'success')
        return render_template('dashboard.html')