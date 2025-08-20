from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from app.decorators import admin_required
from app.models import Subject
from app.models import Sector

subjects = Blueprint('subjects', __name__)

@subjects.route('/view')
@login_required
@admin_required
def view():
    subjects = Subject.query.order_by(Subject.name).all()
    sectors = Sector.query.order_by(Sector.name).all() 
    return render_template('panel/subjects/main.html', subjects=subjects, all_sectors=sectors)

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
