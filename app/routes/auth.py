from flask import Blueprint, render_template, redirect, url_for, flash, request, session
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

    # se o utilizador já existe, faz o login normalmente
    if user:
        login_user(user)
        flash(f'Bem-vindo de volta, {user.username}!', 'success')
        return redirect(url_for('main.home'))
    
    # se o utilizador não existe, cria um novo registo
    else:
        session['google_oauth_email'] = user_info['email']
        session['google_oauth_fname'] = user_info.get('given_name', '')
        session['google_oauth_lname'] = user_info.get('family_name', '')
        
        flash('Bem-vindo! Por favor, complete o seu registo.', 'info')
        return redirect(url_for('auth.complete_google_register'))
    
@auth.route('/complete-google-register', methods=['GET', 'POST'])
def complete_google_register():

    if 'google_oauth_email' not in session:
        flash('Por favor, inicie o registo através da Google.', 'error')
        return redirect(url_for('auth.login'))

    # renderiza o formulário para o método get
    if request.method == 'GET':
        email = session.get('google_oauth_email')
        first_name = session.get('google_oauth_fname')
        last_name = session.get('google_oauth_lname')
        return render_template('cadastro-google.html', email=email, first_name=first_name, last_name=last_name)

    # processa o formulário para o método post
    username = request.form.get('username')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    password = request.form.get('password')

    # validações
    has_error = False
    if not all([username, first_name, last_name, password]):
        flash('Todos os campos são obrigatórios.', 'danger')
        has_error = True

    if User.query.filter_by(username=username).first():
        flash('Este nome de utilizador já está em uso. Por favor, escolha outro.', 'danger')
        has_error = True

    # se houver um erro de validação, renderiza novamente o template com os dados inseridos
    if has_error:
        return render_template('cadastro-google.html',
                               email=session.get('google_oauth_email'), 
                               username=username,
                               first_name=first_name, 
                               last_name=last_name)

    # se a validação passar, cria o novo usuário
    user = User(
        email=session['google_oauth_email'],
        username=username,
        first_name=first_name,
        last_name=last_name
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()

    # limpe os dados temporários da session
    session.pop('google_oauth_email', None)
    session.pop('google_oauth_fname', None)
    session.pop('google_oauth_lname', None)

    # faz o login do novo utilizador e redireciona
    login_user(user)
    flash(f'Registo concluído com sucesso! Bem-vindo, {user.username}!', 'success')
    return render_template('dashboard.html')