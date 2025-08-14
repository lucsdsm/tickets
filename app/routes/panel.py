from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User

panel = Blueprint('panel', __name__)

@panel.route('/view')
@login_required
def view():
    if not current_user.is_admin:
        flash('Acesso negado. Você não tem permissão para acessar o panel de administração.', 'danger')
        return redirect(url_for('main.home'))

    return render_template('panel/index.html', user=current_user)

@panel.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('Acesso negado. Você não tem permissão para acessar a lista de usuários.', 'danger')
        return redirect(url_for('main.home'))

    users = User.query.all()
    return render_template('panel/usuarios.html', users=users)

@panel.route('/edit_user/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('Acesso negado. Você não tem permissão para editar usuários.', 'danger')
        return redirect(url_for('main.home'))

    user = User.query.get_or_404(user_id)

    new_username = request.form.get('username')
    new_first_name = request.form.get('first_name')
    new_last_name = request.form.get('last_name')
    new_email = request.form.get('email')
    new_is_admin = request.form.get('admin') == '1'

    if new_username:
        user.username = new_username
    if new_first_name:
        user.first_name = new_first_name
    if new_last_name:
        user.last_name = new_last_name
    if new_email:
        user.email = new_email
    if new_is_admin is not None:
        # não permitir que admin mude sua própria permissão
        if user.id == current_user.id:
            flash('Você não pode alterar suas próprias permissões de administrador.', 'error')
            return redirect(url_for('panel.users'))
        else:
            user.admin = new_is_admin

    try:
        db.session.commit()
        flash(f'Usuário {user.username} atualizado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar usuário: {str(e)}', 'danger')

    return redirect(url_for('panel.users'))

@panel.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Acesso negado. Você não tem permissão para excluir usuários.', 'danger')
        return redirect(url_for('main.home'))

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Você não pode excluir sua própria conta.', 'error')
        return redirect(url_for('panel.users'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'Usuário {user.username} excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir usuário: {str(e)}', 'danger')

    return redirect(url_for('panel.users'))