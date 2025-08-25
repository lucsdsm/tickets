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

    tickets = db.session.query(Ticket).all()
    return render_template("dashboard/main.html", tickets=tickets)
