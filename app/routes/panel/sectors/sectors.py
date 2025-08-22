from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from app.decorators import admin_required
from app.models import Sector
from app.models import User

sectors = Blueprint('sectors', __name__)

@sectors.route('/view')
@login_required
@admin_required
def view() -> Response:
    """Exibe a lista de setores.

    Esta rota é protegida por login_required e admin_required, o que significa que o usuário
    deve estar autenticado e ser um administrador para acessar esta rota.

    Returns:
        Response: Um objeto de resposta do Flask que renderiza a lista de setores.
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

    sort_column = getattr(Sector, sort_by)
    query = Sector.query.order_by(sort_column.asc() if direction == 'asc' else sort_column.desc())

    sectors = query.all()
    return render_template('panel/sectors/main.html', 
                           sectors=sectors, 
                           sort_by=sort_by, 
                           direction=direction)

@sectors.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add() -> Response:
    """Adiciona um novo setor.

    Esta rota lida com os métodos GET e POST. 
    Para GET, renderiza o formulário de adição de setor.
    Para POST, processa os dados do formulário e cria um novo setor.

    Returns:
        Response: Um objeto de resposta do Flask que redireciona para a lista de setores após a criação.
    """

    if request.method == 'POST':
        name = request.form.get('name')
        color = request.form.get('color')

        has_error = False

        if not all ([name]):
            flash('Todos os campos são obrigatórios.', 'danger')
            has_error = True

        if Sector.query.filter_by(name=name).first():
            flash('Já existe um setor com este nome. Por favor, escolha outro.', 'danger')
            has_error = True

        if has_error:
            return render_template('panel/sectors/add-sector.html', name=name)
        
        else:
            sector = Sector(
                name=name,
                color=color
            )

            db.session.add(sector)
            db.session.commit()

            flash(f'Setor "{sector.name}" cadastrado com sucesso com sucesso.', 'success')
            return redirect(url_for('sectors.view'))
    
    return render_template('panel/sectors/add-sector.html')

@sectors.route('/edit/<int:sector_id>', methods=['POST'])
@login_required
@admin_required
def edit(sector_id) -> Response:
    """Edita um setor existente.

    Esta rota lida com os métodos GET e POST.
    Para GET, renderiza o formulário de edição de setor.
    Para POST, processa os dados do formulário e atualiza o setor existente.

    Returns:
        Response: Um objeto de resposta do Flask que redireciona para a lista de setores após a edição.
    """

    sector = Sector.query.get_or_404(sector_id)

    new_sector_name = request.form.get('name')
    new_sector_color = request.form.get('color')

    if new_sector_name:
        sector.name = new_sector_name

    if new_sector_color:
        sector.color = new_sector_color

    try:
        db.session.commit()
        flash(f'Setor "{sector.name}" atualizado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar setor: {str(e)}', 'danger')

    return redirect(url_for('sectors.view'))

@sectors.route('/delete/<int:sector_id>', methods=['POST'])
@login_required
@admin_required
def delete(sector_id) -> Response:
    """Exclui um setor existente.

    Esta rota lida com o método POST para excluir um setor.
    O setor a ser excluído é identificado pelo seu ID.

    Returns:
        Response: Um objeto de resposta do Flask que redireciona para a lista de setores após a exclusão.
    """
    sector = Sector.query.get_or_404(sector_id)

    try:
        db.session.delete(sector)
        db.session.commit()
        flash(f'Setor "{sector.name}" excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir setor: {str(e)}', 'danger')


    return redirect(url_for('sectors.view'))

@sectors.route('/<int:sector_id>/manage', methods=['GET', 'POST'])
@login_required
@admin_required
def manage(sector_id) -> Response:
    """Gerencia os usuários de um setor.

    Esta rota lida com os métodos GET e POST.
    Para GET, renderiza o formulário de gerenciamento de usuários.
    Para POST, processa os dados do formulário e atualiza os usuários do setor.

    Returns:
        Response: Um objeto de resposta do Flask que redireciona para a lista de setores após a atualização.
    """

    sector = Sector.query.get_or_404(sector_id)

    if request.method == 'POST':
        # obtém a lista de ids dos usuários do setor
        selected_user_ids = request.form.getlist('user_ids')

        # converte os ids de strings para inteiros
        selected_ids_int = [int(id) for id in selected_user_ids]

        # busca os objetos User correspondentes aos ids selecionados
        selected_users = User.query.filter(User.id.in_(selected_ids_int)).all()

        # substitui a lista de usuários do setor pela nova lista
        # o sqlalchemy trata a adição e remoção nas tabelas de junção
        sector.users = selected_users

        db.session.commit()
        flash(f'Membros do setor "{sector.name}" atualizados com sucesso!', 'success')
        return redirect(url_for('sectors.view'))

    # busca todos os usuários para os listar 
    all_users = User.query.order_by(User.username).all()

    return render_template('panel/sectors/manage-users.html', 
                           sector=sector, 
                           all_users=all_users)