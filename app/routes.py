import pandas as pd
from io import BytesIO
from flask import Blueprint, render_template, request, session, redirect, url_for, send_file, jsonify
from app import db
from app.models.user import User
from app.models.water_reading import WaterReading
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            user.visit_count += 1
            user.last_login = datetime.utcnow()
            db.session.commit()
            session.update({
                'user_id': user.id, 'username': user.username,
                'visit_count': user.visit_count,
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M')
            })
            return redirect(url_for('main.index'))
    return render_template('login.html')

@main_bp.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('main.login'))
    return render_template('index.html')

@main_bp.route('/api/data')
def get_data():
    project = request.args.get('project', 'Ocean')
    readings = WaterReading.query.filter_by(project_type=project).all()
    return jsonify([r.to_dict() for r in readings])

@main_bp.route('/export/<project>')
def export_excel(project):
    readings = WaterReading.query.filter_by(project_type=project).all()
    df = pd.DataFrame([r.to_dict() for r in readings])
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name=f"NRSC_{project}_Data.xlsx")

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))
