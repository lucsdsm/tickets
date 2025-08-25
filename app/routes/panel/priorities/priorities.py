from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from app.decorators import admin_required
from app.models import Priority

priorities = Blueprint('priorities', __name__)

@priorities.route('/view')
@login_required
@admin_required
def view() -> Response:
    """Exibe a lista de prioridades.

    Esta rota é protegida por login_required e admin_required, o que significa que o usuário
    deve estar autenticado e ser um administrador para acessar esta rota.

    Returns:
        Response: Um objeto de resposta do Flask que renderiza a lista de prioridades.
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

    sort_column = getattr(Priority, sort_by)
    query = Priority.query.order_by(sort_column.asc() if direction == 'asc' else sort_column.desc())

    priorities = query.all()
    return render_template('panel/priorities/main.html', 
                           priorities=priorities, 
                           sort_by=sort_by, 
                           direction=direction)

@priorities.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add() -> Response:
    """Adiciona uma nova prioridade.

    Esta rota lida com os métodos GET e POST. 
    Para GET, renderiza o formulário de adição de prioridade.
    Para POST, processa os dados do formulário e cria uma nova prioridade.

    Returns:
        Response: Um objeto de resposta do Flask que redireciona para a lista de prioridades após a criação.
    """

    if request.method == 'POST':
        name = request.form.get('name')
        color = request.form.get('color')

        has_error = False

        if not all ([name]):
            flash('Todos os campos são obrigatórios.', 'danger')
            has_error = True

        if Priority.query.filter_by(name=name).first():
            flash('Já existe uma prioridade com este nome. Por favor, escolha outro.', 'danger')
            has_error = True

        if has_error:
            return render_template('panel/priorities/add-priority.html', name=name)

        else:
            priority = Priority(
                name=name,
                color=color
            )

            db.session.add(priority)
            db.session.commit()

            flash(f'Prioridade "{priority.name}" cadastrada com sucesso.', 'success')
            return redirect(url_for('priorities.view'))

    return render_template('panel/priorities/add-priority.html')

@priorities.route('/edit/<int:priority_id>', methods=['POST'])
@login_required
@admin_required
def edit(priority_id) -> Response:
    """Edita uma prioridade existente.

    Esta rota lida com os métodos GET e POST.
    Para GET, renderiza o formulário de edição de prioridade.
    Para POST, processa os dados do formulário e atualiza a prioridade existente.

    Returns:
        Response: Um objeto de resposta do Flask que redireciona para a lista de prioridades após a edição.
    """

    priority = Priority.query.get_or_404(priority_id)

    new_priority_name = request.form.get('name')
    new_priority_color = request.form.get('color')

    if new_priority_name:
        priority.name = new_priority_name

    if new_priority_color:
        priority.color = new_priority_color

    try:
        db.session.commit()
        flash(f'Prioridade "{priority.name}" atualizada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar prioridade: {str(e)}', 'danger')

    return redirect(url_for('priorities.view'))

@priorities.route('/delete/<int:priority_id>', methods=['POST'])
@login_required
@admin_required
def delete(priority_id) -> Response:
    """Exclui uma prioridade existente.

    Esta rota lida com o método POST para excluir uma prioridade.
    A prioridade a ser excluída é identificada pelo seu ID.

    Returns:
        Response: Um objeto de resposta do Flask que redireciona para a lista de prioridades após a exclusão.
    """
    
    priority = Priority.query.get_or_404(priority_id)

    try:
        db.session.delete(priority)
        db.session.commit()
        flash(f'Prioridade "{priority.name}" excluída com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir prioridade: {str(e)}', 'danger')


    return redirect(url_for('priorities.view'))
