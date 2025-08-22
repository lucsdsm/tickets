from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from app.decorators import admin_required
from app.models import Status

statuses = Blueprint('statuses', __name__)

@statuses.route('/view')
@login_required
@admin_required
def view() -> Response:
    """Exibe a lista de statuses.

    Esta rota é protegida por login_required e admin_required, o que significa que o usuário
    deve estar autenticado e ser um administrador para acessar esta rota.

    Returns:
        Response: Um objeto de resposta do Flask que renderiza a lista de statuses.
    """

    # obtém os parâmetros de ordenação da requisição
    sort_by = request.args.get('sort_by', 'id', type=str)
    direction = request.args.get('direction', 'asc', type=str)

    # lista de colunas permitidas para evitar injeção de sql
    allowed_columns = ['id', 'name']

    # valor padrão se a coluna não for permitida
    if sort_by not in allowed_columns: 
        sort_by = 'id'

    # valor padrão se a direção for inválida
    if direction not in ['asc', 'desc']: 
        direction = 'asc'

    sort_column = getattr(Status, sort_by)
    query = Status.query.order_by(sort_column.asc() if direction == 'asc' else sort_column.desc())

    statuses = query.all()
    return render_template('panel/statuses/main.html', 
                           statuses=statuses, 
                           sort_by=sort_by, 
                           direction=direction)

@statuses.route('/add_status', methods=['GET', 'POST'])
@login_required
@admin_required
def add_status() -> Response:
    """Cria um novo status.

    Esta rota é protegida por login_required e admin_required, o que significa que o usuário
    deve estar autenticado e ser um administrador para acessar esta rota.

    Returns:
        Response: Um objeto de resposta do Flask que renderiza o formulário de criação de status.
    """
    
    if request.method == 'POST':
        name = request.form.get('name')
        color = request.form.get('color')

        if name:
            new_status = Status(name=name, color=color)
            db.session.add(new_status)
            db.session.commit()
            flash('Status criado com sucesso!', 'success')
            return redirect(url_for('statuses.view'))
        flash('Nome do status é obrigatório!', 'danger')

    return render_template('panel/statuses/add-status.html')

@statuses.route('/edit_status/<int:status_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_status(status_id: int) -> Response:
    """Edita um status existente.

    Esta rota é protegida por login_required e admin_required, o que significa que o usuário
    deve estar autenticado e ser um administrador para acessar esta rota.

    Args:
        status_id (int): O ID do status a ser editado.

    Returns:
        Response: Um objeto de resposta do Flask que renderiza o formulário de edição de status.
    """
    status = Status.query.get_or_404(status_id)

    if request.method == 'POST':
        name = request.form.get('name')
        color = request.form.get('color')

        if name:
            status.name = name
            status.color = color
            db.session.commit()
            flash('Status editado com sucesso!', 'success')
            return redirect(url_for('statuses.view'))
        flash('Nome do status é obrigatório!', 'danger')

    return render_template('panel/statuses/edit-status.html', status=status)

@statuses.route('/delete_status/<int:status_id>', methods=['POST'])
@login_required
@admin_required
def delete_status(status_id: int) -> Response:
    """Deleta um status existente.

    Esta rota é protegida por login_required e admin_required, o que significa que o usuário
    deve estar autenticado e ser um administrador para acessar esta rota.

    Args:
        status_id (int): O ID do status a ser deletado.

    Returns:
        Response: Um objeto de resposta do Flask que redireciona para a lista de statuses.
    """
    status = Status.query.get_or_404(status_id)
    db.session.delete(status)
    db.session.commit()
    flash('Status deletado com sucesso!', 'success')
    return redirect(url_for('statuses.view'))
