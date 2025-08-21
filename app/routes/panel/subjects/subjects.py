from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from app.decorators import admin_required
from app.models import Subject
from app.models import Sector

subjects = Blueprint('subjects', __name__)

@subjects.route('/view')
@login_required
@admin_required
def view():
    sort_by = request.args.get('sort_by', 'id', type=str)
    direction = request.args.get('direction', 'asc', type=str)

    # lista de colunas permitidas para evitar injeção de sql
    allowed_columns = ['id', 'name', 'sectors']

    if sort_by not in allowed_columns:
        # valor padrão se a coluna não for permitida
        sort_by = 'id'

    if direction not in ['asc', 'desc']:
         # valor padrão se a direção for inválida
        direction = 'asc'
    
    # constrói a query
    query = Subject.query
    if sort_by == 'sectors':
        # para ordenar por setor, faz join nas tabelas assunto e setor.
        # agrupa por utilizador e ordena pelo nome do primeiro setor em ordem alfabética.
        # para ordenar por setor, faz join nas tabelas user e setor. nesse caso faz um left join para recuperar usuários também sem setor.
        # agrupa por utilizador e ordena pelo nome do primeiro setor em ordem alfabética.
        query = query.outerjoin(Subject.sectors).group_by(Subject.id)
        order_expression = func.min(Sector.name)
        
        # .nulls_last() para garantir que os utilizadores sem setor apareçam sempre no final da lista.
        if direction == 'asc':
            query = query.order_by(order_expression.asc().nulls_last())
        else:
            query = query.order_by(order_expression.desc().nulls_last())
    else:
        # ordenação simples.
        sort_column = getattr(Subject, sort_by)
        query = query.order_by(sort_column.asc() if direction == 'asc' else sort_column.desc())
    
    
    subjects = query.all()
    all_sectors = Sector.query.order_by(Sector.name).all()

    return render_template('panel/subjects/main.html', 
                           subjects=subjects, 
                           all_sectors=all_sectors,
                           sort_by=sort_by, 
                           direction=direction)

@subjects.route('/add_subject', methods=['GET', 'POST'])
@login_required
@admin_required
def add_subject():
    if request.method == 'POST':
        name = request.form.get('name')
        selected_sector_ids = request.form.getlist('sectors')

        if name:
            selected_sectors = Sector.query.filter(Sector.id.in_(selected_sector_ids)).all()
            new_subject = Subject(
                name=name, 
                sectors=selected_sectors)

            db.session.add(new_subject)
            db.session.commit()

            flash(f'Assunto "{name}" criado com sucesso!', 'success')
            return redirect(url_for('subjects.view'))
        else:
            flash('O nome do assunto é obrigatório.', 'danger')
            sectors = Sector.query.order_by(Sector.name).all()
            return render_template('panel/subjects/add-subject.html', all_sectors=sectors, name=name)
    
    sectors = Sector.query.order_by(Sector.name).all()
    return render_template('panel/subjects/add-subject.html', all_sectors=sectors)

@subjects.route('/edit/<int:subject_id>', methods=['POST'])
@login_required
@admin_required
def edit_subject(subject_id):
    subject_to_edit = Subject.query.get_or_404(subject_id)

    name = request.form.get('name')
    selected_sector_ids = request.form.getlist('sectors')

    if name:
        subject_to_edit.name = name
        selected_sectors = Sector.query.filter(Sector.id.in_(selected_sector_ids)).all()
        subject_to_edit.sectors = selected_sectors
        db.session.commit()
        flash(f'Assunto "{name}" atualizado com sucesso!', 'success')
    else:
        flash('O nome do assunto é obrigatório.', 'danger')
        
    return redirect(url_for('subjects.view'))

@subjects.route('/delete/<int:subject_id>', methods=['POST'])
@login_required
@admin_required
def delete_subject(subject_id):
    subject_to_delete = Subject.query.get_or_404(subject_id)
    db.session.delete(subject_to_delete)
    db.session.commit()
    flash(f'Assunto "{subject_to_delete.name}" excluído com sucesso.', 'success')
    return redirect(url_for('subjects.view'))
