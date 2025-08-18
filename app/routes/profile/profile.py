from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from app.decorators import admin_required
from app.models import User

profile = Blueprint('profile', __name__)

@profile.route('/view')
@login_required
def view():
    return render_template('profile/main.html')

@profile.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        has_error = False

        if not all([old_password, password, confirm_password]):
            flash('Todos os campos são obrigatórios.', 'danger')
            has_error = True

        if not has_error and not current_user.check_password(old_password):
            flash('A sua senha atual está incorreta.', 'danger')
            has_error = True

        if not has_error and password != confirm_password:
            flash('A nova senha e a confirmação não coincidem.', 'danger')
            has_error = True

        if has_error:
            return render_template('profile/change-password.html')
        
        current_user.set_password(password)
        db.session.commit()
        
        flash('A sua senha foi alterada com sucesso!', 'success')
        return redirect(url_for('profile.view'))
        
    return render_template('profile/change-password.html')