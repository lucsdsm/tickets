from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response, jsonify
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func, or_
from app.decorators import admin_required
from app.models import Ticket
from app.models import User
from app.models import Sector
from app.models import Subject
from app.models import Status
from app.models import Priority

tickets = Blueprint('tickets', __name__)

@tickets.route('/tickets/add', methods=['GET', 'POST'])
@login_required
def add() -> Response:
    """Exibe o formulário para adicionar um novo ticket."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        sector_id = request.form.get('sector_id')
        subject_id = request.form.get('subject_id')
        priority_id = request.form.get('priority_id')

        new_ticket = Ticket(
            title=title,
            description=description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            creator_id=current_user.id,
            sector_id=sector_id,
            subject_id=subject_id,
            priority_id=priority_id,
            status_id=1
        )
        db.session.add(new_ticket)
        db.session.commit()
        flash('Ticket adicionado com sucesso!', 'success')
        return redirect(url_for('dashboard.view'))

    all_sectors = Sector.query.order_by(Sector.name).all()
    all_priorities = Priority.query.order_by(Priority.id).all()

    return render_template('dashboard/tickets/add-ticket.html', 
                           all_sectors=all_sectors,
                           all_priorities=all_priorities)

@tickets.route('/get-subjects-for-sector/<int:sector_id>')
@login_required
def get_subjects_for_sector(sector_id):
    """Retorna uma lista de assuntos (em JSON) para um determinado setor."""
    sector = Sector.query.get_or_404(sector_id)
    subjects_list = [{'id': subject.id, 'name': subject.name} for subject in sector.subjects]
    return jsonify(subjects_list)

