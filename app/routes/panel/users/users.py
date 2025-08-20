from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from app.decorators import admin_required
from app.models import User
from app.models import Sector

users = Blueprint('users', __name__)

@users.route('/view')
@login_required
@admin_required
def view():
    if not current_user.is_admin:
        flash('Acesso negado. Você não tem permissão para acessar a lista de usuários.', 'danger')
        return redirect(url_for('main.home'))

    users = User.query.order_by(User.id).all()
    all_sectors = Sector.query.order_by(Sector.name).all()
    return render_template('panel/users/main.html', users=users, all_sectors=all_sectors)

@users.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    # verifica se o método da requisição é POST
    if request.method == 'POST':
        # obtém os dados do formulário de registro
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        selected_sector_ids = request.form.getlist('sectors')

        # validações
        has_error = False

        # verifica se todos os campos obrigatórios foram preenchidos
        if not all([username, email, first_name, last_name, password]):
            flash('Todos os campos são obrigatórios.', 'danger')
            has_error = True

        if username:
            username = username.strip()
        if email:
            email = email.strip()

        # verificar se o nome de utilizador já está em uso
        if User.query.filter_by(username=username).first():
            flash('Este nome de utilizador já está em uso. Por favor, escolha outro.', 'danger')
            has_error = True

        # verificar se o email já está em uso
        if User.query.filter_by(email=email).first():
            flash('Este email já está em uso. Por favor, escolha outro.', 'danger')
            has_error = True

        # se houver um erro de validação, renderiza novamente o template com os dados inseridos
        if has_error:
            return render_template('panel/users/add-user.html', 
                                   username=username,
                                   email=email,
                                   first_name=first_name, 
                                   last_name=last_name)

        # se a validação passar, cria o novo usuário
        else:
            selected_sectors = Sector.query.filter(Sector.id.in_(selected_sector_ids)).all()

            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                sectors=selected_sectors
            )
            
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            flash(f'Usuário "{user.username}" cadastrado com sucesso com sucesso.', 'success')
            return redirect(url_for('users.view'))

    sectors = Sector.query.order_by(Sector.name).all()
    return render_template('panel/users/add-user.html', all_sectors=sectors)
        

@users.route('/edit_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    new_username = request.form.get('username')
    new_first_name = request.form.get('first_name')
    new_last_name = request.form.get('last_name')
    new_email = request.form.get('email')

    if new_username:
        user.username = new_username
    if new_first_name:
        user.first_name = new_first_name
    if new_last_name:
        user.last_name = new_last_name
    if new_email:
        user.email = new_email
    if user.id == current_user.id:
        # não permitir o administrador remover sua própria permissão
        if 'admin' in request.form and user.admin and not (request.form.get('admin') == '1'):
            flash('Você não pode remover suas permissões de administrador. Por favor, contacte a equipe de desenvolvimento do sistema.', 'danger')
            return redirect(url_for('users.view'))
    else:
        user.admin = 'admin' in request.form and request.form.get('admin') == '1'

    try:
        selected_sector_ids = request.form.getlist('sectors')
    
        # converte a lista de ids que são strings para inteiros
        selected_ids_int = [int(id) for id in selected_sector_ids]
        
        # busca os objetos sector correspondentes aos ids selecionados
        selected_sectors = Sector.query.filter(Sector.id.in_(selected_ids_int)).all()
        
        # atribui a nova lista de setores à relação do utilizador
        user.sectors = selected_sectors

        db.session.commit()
        flash(f'Usuário "{user.username}" atualizado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar usuário: {str(e)}', 'danger')

    return redirect(url_for('users.view'))

@users.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Você não pode excluir sua própria conta.', 'error')
        return redirect(url_for('users.view'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'Usuário "{user.username}" excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir usuário: {str(e)}', 'danger')

    return redirect(url_for('users.view'))