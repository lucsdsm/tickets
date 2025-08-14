from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db, bcrypt, oauth

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register() -> 'Response':
    """Processa o formulário de registro do utilizador.

    Esta rota lida com os métodos GET e POST. Para GET, simplesmente renderiza
    o template de registro. Para POST, valida os dados do formulário,
    cria um novo utilizador na base de dados e inicia uma sessão para o
    utilizador recém-registrado.

    Returns:
        Response: Um objeto de resposta do Flask. Pode ser o template de registro
                  renderizado ou um redirecionamento para a página inicial.
    """

    # se o usuário já estiver logado, redireciona para a página de tickets
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # verifica se o método da requisição é POST
    if request.method == 'POST':
        # obtém os dados do formulário de registro
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password')

        # validações
        has_error = False

        # verifica se todos os campos obrigatórios foram preenchidos
        if not all([username, email, first_name, last_name, password]):
            flash('Todos os campos são obrigatórios.', 'danger')
            has_error = True

        # verificar se o nome de utilizador já está em uso
        if User.query.filter_by(username=username).first():
            flash('Este nome de utilizador já está em uso. Por favor, escolha outro.', 'danger')
            has_error = True

        # verificar se o email já está em uso
        if User.query.filter_by(email=email).first():
            flash('Este email já está em uso. Por favor, escolha outro.', 'danger')
            has_error = True

        # verificar se a senha é igual ao campo de confirmação
        if password != confirm_password:
            flash('As senhas não coincidem. Por favor, tente novamente.', 'danger')
            has_error = True

        # se houver um erro de validação, renderiza novamente o template com os dados inseridos
        if has_error:
            return render_template('cadastro-local.html', 
                                   username=username,
                                   email=email,
                                   first_name=first_name, 
                                   last_name=last_name)

        # se a validação passar, cria o novo usuário
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # faz o login do novo utilizador e redireciona
        login_user(user)
        flash(f'Registro concluído com sucesso! Bem-vindo, {user.username}!', 'success')
        return render_template('dashboard.html')
    
    # se o método for GET, renderiza o template de registro
    return render_template('cadastro-local.html')

@auth.route('/login', methods=['GET', 'POST'])
def login() -> 'Response': 
    """Processa o formulário de login do utilizador.

    Esta rota lida com os métodos GET e POST. Para GET, simplesmente renderiza
    o template de login. Para POST, valida as credenciais do utilizador
    (email e senha) contra a base de dados. Se as credenciais forem
    válidas, inicia uma sessão para o utilizador. Caso contrário, exibe
    uma mensagem de erro.

    Returns:
        Response: Um objeto de resposta do Flask. Pode ser o template de login
                  renderizado ou um redirecionamento para a página inicial.
    """

    # se o usuário já estiver logado, redireciona para a página de tickets
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
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
    
    # se o método for GET, renderiza o template de login
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout() -> 'Response':
    """Desconecta o utilizador da sessão atual.

    Esta rota é protegida por login_required, o que significa que o utilizador
    deve estar autenticado para acessar esta rota. Quando acessada, a sessão
    do utilizador é encerrada e o utilizador é redirecionado para a página inicial
    com uma mensagem de sucesso.

    Returns:
        Response: Um objeto de resposta do Flask que redireciona para a página inicial.
    """

    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.home'))

@auth.route('/google/login')
def google_login() -> 'Response':
    """Inicia o processo de autenticação com a Google.

    Esta rota redireciona o utilizador para a página de autenticação da Google.
    O utilizador será redirecionado de volta para a rota de callback após a autenticação.

    Returns:
        Response: Um objeto de resposta do Flask que redireciona para a página de autenticação da Google.
    """

    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth.route('/google/callback')
def google_callback() -> 'Response':
    """Processa o callback da autenticação com a Google.

    Esta rota é chamada pela Google após o utilizador autenticar-se. Ela obtém
    as informações do utilizador e verifica se o utilizador já existe na base de dados.
    Se o utilizador existir, faz o login. Caso contrário, redireciona para a página de registro
    para completar o registro.

    Returns:
        Response: Um objeto de resposta do Flask que redireciona para a página inicial ou para a página de registro.
    """
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
    
    # se o utilizador não existe, cria um novo registro
    else:
        session['google_oauth_email'] = user_info['email']
        session['google_oauth_fname'] = user_info.get('given_name', '')
        session['google_oauth_lname'] = user_info.get('family_name', '')
        
        flash('Bem-vindo! Por favor, complete o seu registro.', 'info')
        return redirect(url_for('auth.complete_google_register'))
    
@auth.route('/complete-google-register', methods=['GET', 'POST'])
def complete_google_register() -> 'Response':

    """Completa o registro do utilizador após a autenticação com a Google.
    
    Esta rota lida com os métodos GET e POST. Para GET, renderiza o formulário de registro
    pré-preenchido com os dados obtidos da Google. Para POST, processa o formulário,
    valida os dados e cria um novo utilizador na base de dados.
    
    Returns:
        Response: Um objeto de resposta do Flask. Pode ser o template de registro renderizado ou um redirecionamento para a página inicial.
    """

    if 'google_oauth_email' not in session:
        flash('Por favor, inicie o registro através da Google.', 'error')
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
    confirm_password = request.form.get('confirm_password')

    # validações
    has_error = False

    # verifica se todos os campos obrigatórios foram preenchidos
    if not all([username, first_name, last_name, password]):
        flash('Todos os campos são obrigatórios.', 'danger')
        has_error = True

    # verificar se o nome de utilizador já está em uso
    if User.query.filter_by(username=username).first():
        flash('Este nome de utilizador já está em uso. Por favor, escolha outro.', 'danger')
        has_error = True
    
    # verificar se a senha é igual ao campo de confirmação
    if password != confirm_password:
        flash('As senhas não coincidem. Por favor, tente novamente.', 'danger')
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
    flash(f'registro concluído com sucesso! Bem-vindo, {user.username}!', 'success')
    return render_template('dashboard.html')