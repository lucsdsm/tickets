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

    sectors = Sector.query.order_by(Sector.id).all()
    return render_template('panel/sectors/main.html', sectors=sectors)

@sectors.route('/add_sector', methods=['GET', 'POST'])
@login_required
@admin_required
def add_sector():
    return redirect(url_for('sectors.view'))

@sectors.route('/edit_sector/<int:sector_id>', methods=['POST'])
@login_required
@admin_required
def edit_sector(sector_id):
    return redirect(url_for('sectors.view'))

@sectors.route('/delete_sector/<int:sector_id>', methods=['POST'])
@login_required
@admin_required
def delete_sector(sector):
    return redirect(url_for('sectors.view'))