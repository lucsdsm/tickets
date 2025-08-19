from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from app.decorators import admin_required
from app.models import Sector

sectors = Blueprint('sectors', __name__)

@sectors.route('/view')
@login_required
@admin_required
def view():
    if not current_user.is_admin:
        flash('Acesso negado. Você não tem permissão para acessar a lista de setores.', 'danger')
        return redirect(url_for('main.home'))

    sectors = Sector.query.order_by(Sector.name).all()
    return render_template('panel/sectors/main.html', sectors=sectors)

@sectors.route('/add_sector', methods=['GET', 'POST'])
@login_required
@admin_required
def add_sector():
    if request.method == 'POST':
        name = request.form['name']

        has_error = False

        if not all ([name]):
            flash('Todos os campos são obrigatórios.', 'danger')
            has_error = True

        if Sector.query.filter_by(name=name).first():
            flash('Já existe um setor com este nome. Por favor, escolha outro.', 'danger')
            has_error = True

        if has_error:
            return render_template('panel/sectors/add-sector.html',
                                name=name)
        
        else:
            sector = Sector(
                name=name
            )

            db.session.add(sector)
            db.session.commit()

            flash(f'Setor "{sector.name}" cadastrado com sucesso com sucesso.', 'success')
            return redirect(url_for('sectors.view'))
    
    return render_template('panel/sectors/add-sector.html')

@sectors.route('/edit_sector/<int:sector_id>', methods=['POST'])
@login_required
@admin_required
def edit_sector(sector_id):
    sector = Sector.query.get_or_404(sector_id)

    new_sector_name = request.form.get('name')

    if new_sector_name:
        sector.name = new_sector_name

    try:
        db.session.commit()
        flash(f'Setor "{sector.name}" atualizado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar setor: {str(e)}', 'danger')

    return redirect(url_for('sectors.view'))

@sectors.route('/delete_sector/<int:sector_id>', methods=['POST'])
@login_required
@admin_required
def delete_sector(sector_id):
    sector = Sector.query.get_or_404(sector_id)

    try:
        db.session.delete(sector)
        db.session.commit()
        flash(f'Setor "{sector.name}" excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir setor: {str(e)}', 'danger')


    return redirect(url_for('sectors.view'))