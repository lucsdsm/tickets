from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from app.decorators import admin_required
from app.models import User

panel = Blueprint('panel', __name__)

@panel.route('/view')
@login_required
@admin_required
def view() -> 'Response':
    """Exibe o painel de administração.
    
    Esta rota é protegida por login_required e admin_required, o que significa que o utilizador
    deve estar autenticado e ser um administrador para acessar esta rota.

    Returns:
        Response: Um objeto de resposta do Flask que renderiza o painel de administração.
    """

    if not current_user.is_admin:
        flash('Acesso negado. Você não tem permissão para acessar o panel de administração.', 'danger')
        return redirect(url_for('main.home'))

    return render_template('panel/main.html', user=current_user)

