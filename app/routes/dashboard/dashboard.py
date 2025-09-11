from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func, or_
from app.decorators import admin_required
from app.models import Ticket
from app.models import User
from app.models import Sector
from app.models import Subject
from app.models import Status
from app.models import Priority

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/user_tickets')
@login_required
def user_tickets() -> Response:
    """Exibe uma lista de tickets com filtros e ordenação."""

    # ------------------------------
    # contadores
    # ------------------------------
    open_status_ids = [s.id for s in Status.query.filter(Status.name != 'Resolvido').all()]
    open_user_tickets_count = Ticket.query.filter(
        Ticket.creator_id == current_user.id,
        Ticket.status_id.in_(open_status_ids)
    ).count()

    working_status_ids = [s.id for s in Status.query.filter(Status.name.in_(['Em Progresso', 'Editado'])).all()]
    assigned_user_tickets_count = Ticket.query.filter(
        Ticket.assignee_id == current_user.id,
        Ticket.status_id.in_(working_status_ids)
    ).count()

    user_sector_ids = [sector.id for sector in current_user.sectors]

    # ------------------------------
    # ordenação
    # ------------------------------
    sort_by = request.args.get('sort_by', 'id', type=str)
    direction = request.args.get('direction', 'asc', type=str)

    allowed_columns = ['id', 'title', 'sector', 'subject', 'creator', 'created_at', 'status']
    if sort_by not in allowed_columns:
        sort_by = 'id'

    if direction not in ['asc', 'desc']:
        direction = 'asc'

    # Query base com ordenação
    base_query = Ticket.query
    if sort_by == 'sector':
        base_query = base_query.join(Sector).order_by(
            Sector.name.asc() if direction == 'asc' else Sector.name.desc()
        )

    elif sort_by == 'subject':
        base_query = base_query.join(Subject).order_by(
            Subject.name.asc() if direction == 'asc' else Subject.name.desc()
        )

    elif sort_by == 'creator':
        base_query = base_query.join(User, User.id == Ticket.creator_id).order_by(
            User.first_name.asc() if direction == 'asc' else User.first_name.desc()
        )
        
    elif sort_by == 'created_at':
        base_query = base_query.order_by(
            Ticket.created_at.asc() if direction == 'asc' else Ticket.created_at.desc()
        )
    
    elif sort_by == 'status':
        base_query = base_query.join(Status).order_by(
            Status.name.asc() if direction == 'asc' else Status.name.desc()
        )

    else:
        sort_column = getattr(Ticket, sort_by)
        base_query = base_query.order_by(
            sort_column.asc() if direction == 'asc' else sort_column.desc()
        )

    # ------------------------------
    # queries finais (apenas filtros)
    # ------------------------------

    # filtro de tickets do usuário
    user_tickets = base_query.filter(
        (Ticket.creator_id == current_user.id) | (Ticket.assignee_id == current_user.id)
    ).all()

    # ------------------------------
    # render
    # ------------------------------
    return render_template(
        "dashboard/user-tickets.html",
        user_tickets=user_tickets,
        open_user_tickets_count=open_user_tickets_count,
        assigned_user_tickets_count=assigned_user_tickets_count,
        sort_by=sort_by,
        direction=direction
    )

@dashboard.route('/sector_user_tickets')
@login_required
def sector_user_tickets() -> Response:
    """Exibe uma lista de tickets com filtros e ordenação."""

    # ------------------------------
    # contadores
    # ------------------------------
    user_sector_ids = [sector.id for sector in current_user.sectors]
    open_sector_status_ids = [s.id for s in Status.query.filter(Status.name.in_(['Aberto', 'Aguardando'])).all()]

    sector_user_tickets_count = 0
    if user_sector_ids:
        sector_user_tickets_count = Ticket.query.filter(
            Ticket.sector_id.in_(user_sector_ids),
            Ticket.status_id.in_(open_sector_status_ids)
        ).count()

    # ------------------------------
    # ordenação
    # ------------------------------
    sort_by = request.args.get('sort_by', 'id', type=str)
    direction = request.args.get('direction', 'asc', type=str)

    allowed_columns = ['id', 'title', 'sector', 'subject', 'creator', 'created_at', 'status']
    if sort_by not in allowed_columns:
        sort_by = 'id'

    if direction not in ['asc', 'desc']:
        direction = 'asc'

    # Query base com ordenação
    base_query = Ticket.query
    if sort_by == 'sector':
        base_query = base_query.join(Sector).order_by(
            Sector.name.asc() if direction == 'asc' else Sector.name.desc()
        )

    elif sort_by == 'subject':
        base_query = base_query.join(Subject).order_by(
            Subject.name.asc() if direction == 'asc' else Subject.name.desc()
        )

    elif sort_by == 'creator':
        base_query = base_query.join(User, User.id == Ticket.creator_id).order_by(
            User.first_name.asc() if direction == 'asc' else User.first_name.desc()
        )
        
    elif sort_by == 'created_at':
        base_query = base_query.order_by(
            Ticket.created_at.asc() if direction == 'asc' else Ticket.created_at.desc()
        )
    
    elif sort_by == 'status':
        base_query = base_query.join(Status).order_by(
            Status.name.asc() if direction == 'asc' else Status.name.desc()
        )

    else:
        sort_column = getattr(Ticket, sort_by)
        base_query = base_query.order_by(
            sort_column.asc() if direction == 'asc' else sort_column.desc()
        )

    # ------------------------------
    # queries finais (apenas filtros)
    # ------------------------------

    # filtro de tickets do setor do usuário
    sector_user_tickets = []
    if user_sector_ids:
        sector_user_tickets = base_query.filter(
            Ticket.sector_id.in_(user_sector_ids),
            Ticket.status_id.in_([1, 2])
        ).all()

    # ------------------------------
    # render
    # ------------------------------
    return render_template(
        "dashboard/sector-user-tickets.html",
        sector_user_tickets=sector_user_tickets,
        sector_user_tickets_count=sector_user_tickets_count,
        sort_by=sort_by,
        direction=direction
    )
