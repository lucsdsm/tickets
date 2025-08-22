from flask import Blueprint, render_template, Response
from flask import redirect, url_for
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route('/')
def home() -> Response:
    """Exibe a página inicial ou o painel do utilizador logado."""

    # se o usuário estiver logado, redireciona para a página de tickets
    if current_user.is_authenticated:
        return render_template('dashboard.html')
    # caso contrário, renderiza a página inicial
    else:
        return render_template('index.html')
