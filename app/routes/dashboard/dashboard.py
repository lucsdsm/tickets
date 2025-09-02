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

@dashboard.route('/tickets')
@login_required
def view() -> Response:
    """Exibe uma lista de tickets.

    Esta rota exibe uma lista de tickets com opções de pesquisa e ordenação.
    Os tickets podem ser filtrados por nome, email e outros critérios.

    Returns:
        Response: Template de visualização de tickets.
    """

    # Chamados abertos pelo usuário atual.
    ###
    # Encontra os status que não são "Resolvido".
    open_statuses = Status.query.filter(Status.name != 'Resolvido').all()
    # Obtém os IDs dos status encontrados.
    open_status_ids = [s.id for s in open_statuses]
    # Faz a contagem de tickets abertos pelo usuário atual que tenham um desses status.
    open_user_tickets_count = Ticket.query.filter(
        Ticket.creator_id == current_user.id,
        Ticket.status_id.in_(open_status_ids)
    ).count()
    ###

    # Chamados atribuídos ao usuário atual.
    ###
    # Encontra o status "Em Progresso" e "Editado".
    working_statuses = Status.query.filter(Status.name.in_(['Em Progresso', 'Editado'])).all()
    # Obtém os IDs dos status encontrados.
    working_status_ids = [s.id for s in working_statuses]
    # Faz a contagem de tickets atribuídos ao usuário atual que tenham um desses status.
    assigned_user_tickets_count = Ticket.query.filter(
        Ticket.assignee_id == current_user.id,
        Ticket.status_id.in_(working_status_ids)
    ).count()
    ###

    # Chamados abertos no setor do usuário atual.
    ###
    # Obtém a lista ed Ids de todos os setores do usuário atual.
    user_sector_ids = [sector.id for sector in current_user.sectors]
    # Encontra o status "Aberto" e "Aguardando".
    open_statuses = Status.query.filter(Status.name.in_(['Aberto', 'Aguardando'])).all()
    # Obtém os IDs dos status encontrados.
    open_status_ids = [s.id for s in open_statuses]
    # Faz a contagem dos tickets que pertencem a qualquer um desses setores.
    sector_user_tickets_count = 0
    # Só executa a query se o usuário pertencer a algum setor.
    if user_sector_ids:
        sector_user_tickets_count = Ticket.query.filter(
            Ticket.sector_id.in_(user_sector_ids),
            Ticket.status_id.in_(open_status_ids)
        ).count()
    ###

    tickets = db.session.query(Ticket).all()

    # Filtrar os tickets para incluir apenas àqueles criados ou aceitos pelo usuário.
    user_tickets = [ticket for ticket in tickets if ticket.creator_id == current_user.id or ticket.assignee_id == current_user.id]

    # Filtrar os tickets para incluir apenas aqueles do setor do usuário que estejam com status_id = 1 ou = 2:
    sector_user_tickets = [ticket for ticket in tickets if ticket.sector_id in user_sector_ids and ticket.status_id in [1, 2]]


    return render_template("dashboard/main.html",
                           user_tickets=user_tickets,
                           sector_user_tickets=sector_user_tickets,
                           open_user_tickets_count=open_user_tickets_count,
                           assigned_user_tickets_count=assigned_user_tickets_count,
                           sector_user_tickets_count=sector_user_tickets_count)
