from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app import db
from app.models import WaterReading, User
from datetime import datetime, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from io import BytesIO
import json
from functools import wraps
from werkzeug.utils import secure_filename
import os

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# ==================== Authentication Decorator ====================

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== Authentication Routes ====================

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and authentication"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template('login.html', error='Username and password are required')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            return render_template('login.html', error='Invalid username or password')
        
        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('main.index'))
    
    # Check if already logged in
    if 'user_id' in session:
        return redirect(url_for('main.index'))
    
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('main.login'))

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not password or not confirm_password:
            return render_template('register.html', error='All fields are required')
        
        if len(username) < 3 or len(username) > 30:
            return render_template('register.html', error='Username must be 3-30 characters')
        
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists. Please choose another.')
        
        # Create new user
        try:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            return render_template('register.html', success='Account created successfully! Please log in.')
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error=f'Error creating account: {str(e)}')
    
    # Check if already logged in
    if 'user_id' in session:
        return redirect(url_for('main.index'))
    
    return render_template('register.html')

@main_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password for logged-in user"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Get current user
        user = User.query.get(session['user_id'])
        
        if not user:
            return render_template('change_password.html', error='User not found')
        
        # Verify current password
        if not user.check_password(current_password):
            return render_template('change_password.html', error='Current password is incorrect')
        
        # Validate new password
        if len(new_password) < 6:
            return render_template('change_password.html', error='New password must be at least 6 characters')
        
        if new_password != confirm_password:
            return render_template('change_password.html', error='New passwords do not match')
        
        if current_password == new_password:
            return render_template('change_password.html', error='New password must be different from current password')
        
        # Update password
        try:
            user.set_password(new_password)
            db.session.commit()
            return render_template('change_password.html', success='Password changed successfully!')
        except Exception as e:
            db.session.rollback()
            return render_template('change_password.html', error=f'Error changing password: {str(e)}')
    
    return render_template('change_password.html')

# ==================== Web Routes ====================

@main_bp.route('/')
@login_required
def index():
    """Home page with data dashboard"""
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    """Real-time monitoring dashboard"""
    return render_template('dashboard.html')

# ==================== API Authentication Helper ====================

def api_login_required(f):
    """Decorator to check if user is logged in for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized - Please login first'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==================== API Routes ====================

@api_bp.route('/readings', methods=['GET'])
@api_login_required
def get_readings():
    """Get all water quality readings with filtering and sorting"""
    try:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Filtering
        water_type = request.args.get('water_type', None)
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        # Sorting
        sort_by = request.args.get('sort_by', 'timestamp')
        sort_order = request.args.get('sort_order', 'desc')
        
        query = WaterReading.query
        
        # Apply filters
        if water_type:
            query = query.filter_by(water_type=water_type)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(WaterReading.timestamp >= start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(WaterReading.timestamp <= end_dt)
            except ValueError:
                pass
        
        # Apply sorting
        if hasattr(WaterReading, sort_by):
            sort_column = getattr(WaterReading, sort_by)
            if sort_order.lower() == 'asc':
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(WaterReading.timestamp.desc())
        
        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [reading.to_dict() for reading in paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/reading', methods=['POST'])
@api_login_required
def create_reading():
    """Create a new water quality reading from IoT sensor"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['latitude', 'longitude', 'water_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create new reading
        reading = WaterReading(
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat())),
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            water_type=data['water_type'],
            chlorophyll=float(data.get('chlorophyll')) if data.get('chlorophyll') else None,
            pigments=float(data.get('pigments')) if data.get('pigments') else None,
            total_alkalinity=float(data.get('total_alkalinity')) if data.get('total_alkalinity') else None,
            dic=float(data.get('dic')) if data.get('dic') else None,
            temperature=float(data.get('temperature')) if data.get('temperature') else None,
            sensor_id=data.get('sensor_id', None)
        )
        
        db.session.add(reading)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reading created successfully',
            'data': reading.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid data format: {str(e)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/reading/<int:reading_id>', methods=['GET'])
@api_login_required
def get_reading(reading_id):
    """Get a specific reading by ID"""
    try:
        reading = WaterReading.query.get_or_404(reading_id)
        return jsonify({
            'success': True,
            'data': reading.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@api_bp.route('/reading/<int:reading_id>', methods=['PUT'])
@api_login_required
def update_reading(reading_id):
    """Update a water quality reading"""
    try:
        reading = WaterReading.query.get_or_404(reading_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'chlorophyll' in data:
            reading.chlorophyll = float(data['chlorophyll']) if data['chlorophyll'] else None
        if 'pigments' in data:
            reading.pigments = float(data['pigments']) if data['pigments'] else None
        if 'total_alkalinity' in data:
            reading.total_alkalinity = float(data['total_alkalinity']) if data['total_alkalinity'] else None
        if 'dic' in data:
            reading.dic = float(data['dic']) if data['dic'] else None
        if 'temperature' in data:
            reading.temperature = float(data['temperature']) if data['temperature'] else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reading updated successfully',
            'data': reading.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/reading/<int:reading_id>', methods=['DELETE'])
@api_login_required
def delete_reading(reading_id):
    """Delete a water quality reading"""
    try:
        reading = WaterReading.query.get_or_404(reading_id)
        db.session.delete(reading)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reading deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/export/excel', methods=['GET'])
@api_login_required
def export_excel():
    """Export water quality readings to Excel format"""
    try:
        # Get all readings
        water_type = request.args.get('water_type', None)
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        query = WaterReading.query
        
        if water_type:
            query = query.filter_by(water_type=water_type)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(WaterReading.timestamp >= start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(WaterReading.timestamp <= end_dt)
            except ValueError:
                pass
        
        readings = query.order_by(WaterReading.timestamp.desc()).all()
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Water Quality Data"
        
        # Define headers
        headers = ['Date', 'Time', 'Latitude', 'Longitude', 'Water Type', 
                   'Chlorophyll (mg/L)', 'Pigments (mg/L)', 'Total Alkalinity (mg/L)', 
                   'DIC (mmol/L)', 'Temperature (°C)', 'Sensor ID']
        
        # Style headers
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        # Add headers
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # Add data rows
        for row_idx, reading in enumerate(readings, 2):
            ws.cell(row=row_idx, column=1).value = reading.timestamp.strftime('%Y-%m-%d')
            ws.cell(row=row_idx, column=2).value = reading.timestamp.strftime('%H:%M:%S')
            ws.cell(row=row_idx, column=3).value = round(reading.latitude, 6)
            ws.cell(row=row_idx, column=4).value = round(reading.longitude, 6)
            ws.cell(row=row_idx, column=5).value = reading.water_type
            ws.cell(row=row_idx, column=6).value = reading.chlorophyll
            ws.cell(row=row_idx, column=7).value = reading.pigments
            ws.cell(row=row_idx, column=8).value = reading.total_alkalinity
            ws.cell(row=row_idx, column=9).value = reading.dic
            ws.cell(row=row_idx, column=10).value = reading.temperature
            ws.cell(row=row_idx, column=11).value = reading.sensor_id
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 16
        ws.column_dimensions['G'].width = 16
        ws.column_dimensions['H'].width = 18
        ws.column_dimensions['I'].width = 14
        ws.column_dimensions['J'].width = 16
        ws.column_dimensions['K'].width = 15
        
        # Save to bytes
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Return file
        from flask import send_file
        filename = f"water_quality_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stats', methods=['GET'])
@api_login_required
def get_stats():
    """Get statistics about water quality readings"""
    try:
        total_readings = WaterReading.query.count()
        water_types = db.session.query(WaterReading.water_type).distinct().count()
        
        # Get latest reading
        latest = WaterReading.query.order_by(WaterReading.timestamp.desc()).first()
        
        # Get average values
        from sqlalchemy import func
        avg_temp = db.session.query(func.avg(WaterReading.temperature)).scalar()
        avg_chlorophyll = db.session.query(func.avg(WaterReading.chlorophyll)).scalar()
        
        return jsonify({
            'success': True,
            'data': {
                'total_readings': total_readings,
                'water_types_count': water_types,
                'latest_reading': latest.to_dict() if latest else None,
                'average_temperature': round(avg_temp, 2) if avg_temp else None,
                'average_chlorophyll': round(avg_chlorophyll, 2) if avg_chlorophyll else None
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/locations', methods=['GET'])
@api_login_required
def get_locations():
    """Get all unique measurement locations"""
    try:
        locations = db.session.query(
            WaterReading.latitude,
            WaterReading.longitude,
            WaterReading.water_type
        ).distinct().all()
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'latitude': round(loc[0], 6),
                    'longitude': round(loc[1], 6),
                    'water_type': loc[2]
                }
                for loc in locations
            ]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/sensor/data', methods=['POST'])
@api_login_required
def receive_sensor_data():
    """Receive real-time data from external IoT sensor hardware"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['latitude', 'longitude', 'water_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create new reading from sensor
        reading = WaterReading(
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat())),
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            water_type=data['water_type'],
            chlorophyll=float(data.get('chlorophyll')) if data.get('chlorophyll') else None,
            pigments=float(data.get('pigments')) if data.get('pigments') else None,
            total_alkalinity=float(data.get('total_alkalinity')) if data.get('total_alkalinity') else None,
            dic=float(data.get('dic')) if data.get('dic') else None,
            temperature=float(data.get('temperature')) if data.get('temperature') else None,
            sensor_id=data.get('sensor_id', 'HARDWARE-SENSOR')
        )
        
        db.session.add(reading)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sensor data received and stored',
            'data': reading.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid data format: {str(e)}'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/sensor/latest', methods=['GET'])
@api_login_required
def get_latest_sensor_data():
    """Get latest sensor data for real-time display"""
    try:
        latest = WaterReading.query.order_by(WaterReading.timestamp.desc()).first()
        
        if not latest:
            return jsonify({
                'success': True,
                'data': None,
                'message': 'No sensor data available'
            }), 200
        
        return jsonify({
            'success': True,
            'data': latest.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
