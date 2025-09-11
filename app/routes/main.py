from flask import Blueprint, render_template, Response
from flask import redirect, url_for
from flask_login import current_user
main = Blueprint('main', __name__)

@main.route('/')
def home() -> Response:
    """Exibe a página inicial ou o painel do usuário logado."""

    # se o usuário estiver logado, redireciona para a página de tickets
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.user_tickets'))
    # caso contrário, renderiza a página de login
    return redirect(url_for('auth.login'))
