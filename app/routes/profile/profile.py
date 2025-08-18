from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from app.decorators import admin_required
from app.models import User

profile = Blueprint('profile', __name__)

@profile.route('/view')
@login_required
def view():
    return render_template('profile/main.html')