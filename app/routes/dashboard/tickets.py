from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response, jsonify, abort
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
from app.models import TicketMessage

tickets = Blueprint('tickets', __name__)

@tickets.route('/view/<int:ticket_id>')
@login_required
def view_ticket(ticket_id: int) -> Response:
    """Exibe os detalhes de um ticket específico, apenas se o usuário tiver acesso."""
    ticket = Ticket.query.get_or_404(ticket_id)

    # verifica se o usuário tem permissão para acessar o ticket
    ## se o usuário não for o criador, o responsável ou um administrador, redireciona de volta para o dashboard com um erro.
    if ticket.creator_id != current_user.id and ticket.assignee_id != current_user.id and not current_user.is_admin:
        # verificar se o usuário está no setor do ticket ou é admin
        if not current_user.is_admin:
            user_sectors = [sector.id for sector in current_user.sectors]
            if ticket.sector_id not in user_sectors:
                flash('Você não tem permissão para acessar este ticket.', 'danger')
                return redirect(url_for('dashboard.user_tickets'))
    
    messages = TicketMessage.query.filter_by(ticket_id=ticket.id).order_by(TicketMessage.created_at.asc()).all()
    return render_template('dashboard/tickets/view-ticket.html', ticket=ticket, messages=messages)

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
        return redirect(url_for('dashboard.user_tickets'))

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

@tickets.route('/tickets/assign/<int:ticket_id>', methods=['POST'])
@login_required
def assign_ticket(ticket_id: int) -> Response:
    """Atribui um ticket a um usuário específico."""
    ticket = Ticket.query.get_or_404(ticket_id)

    if ticket.assignee_id is not None:
        flash('Este ticket já está atribuído.', 'warning')
        return redirect(url_for('dashboard.user_tickets'))
    
    ticket.status_id = 3
    ticket.assignee_id = current_user.id
    ticket.assigned_at = datetime.utcnow()
    ticket.updated_at = datetime.utcnow()
    db.session.commit()
    flash('Ticket atribuído com sucesso!', 'success')
    return redirect(url_for('dashboard.user_tickets'))

@tickets.route('/tickets/<int:ticket_id>/chat', methods=['GET', 'POST'])
@login_required
def chat(ticket_id: int) -> Response:
    """Exibe o chat de um ticket específico."""

    # pega o ticket ou retorna 404
    ticket = Ticket.query.get_or_404(ticket_id)

    # verifica se o usuário tem permissão
    if ticket.creator_id != current_user.id and ticket.assignee_id != current_user.id and not current_user.is_admin:
        flash('Você não tem permissão para acessar o chat deste ticket.', 'danger')
        return redirect(url_for('dashboard.user_tickets'))

    # se for post, envia mensagem
    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            new_message = TicketMessage(
                message=message,
                ticket_id=ticket.id,
                author_id=current_user.id
            )
            db.session.add(new_message)
            db.session.commit()
            flash('Mensagem enviada com sucesso!', 'success')
        else:
            flash('Mensagem não pode ser vazia.', 'danger')

    # Carrega todas as mensagens do ticket
    messages = TicketMessage.query.filter_by(ticket_id=ticket.id).order_by(TicketMessage.created_at.asc()).all()

    return render_template(
        'dashboard/tickets/view-ticket.html',
        ticket=ticket,
        messages=messages
    )

