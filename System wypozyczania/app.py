import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# MODELE
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    image_file = db.Column(db.String(120), nullable=True)
    is_reserved = db.Column(db.Boolean, default=False)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    user = db.relationship('User', backref=db.backref('reservations', lazy=True))
    equipment = db.relationship('Equipment', backref=db.backref('reservations', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# STRONY
@app.route('/')
def index():
    equipment = Equipment.query.all()
    return render_template('index.html', equipment=equipment)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        user = User(username=username, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Rejestracja udana!', 'success')
            return redirect(url_for('login'))
        except:
            flash('Błąd rejestracji. Spróbuj inną nazwę.', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Błędne dane logowania.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Brak dostępu.', 'danger')
        return redirect(url_for('index'))
    equipment = Equipment.query.all()
    return render_template('admin.html', equipment=equipment)

@app.route('/add_equipment', methods=['GET', 'POST'])
@login_required
def add_equipment():
    if not current_user.is_admin:
        flash('Brak dostępu.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image = request.files.get('image')
        image_filename = None
        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        new_equipment = Equipment(name=name, description=description, image_file=image_filename)
        db.session.add(new_equipment)
        db.session.commit()
        flash('Sprzęt dodany!', 'success')
        return redirect(url_for('index'))
    return render_template('add_equipment.html')

@app.route('/edit_equipment/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_equipment(id):
    if not current_user.is_admin:
        flash('Brak dostępu.', 'danger')
        return redirect(url_for('index'))

    equipment = Equipment.query.get_or_404(id)
    if request.method == 'POST':
        equipment.name = request.form['name']
        equipment.description = request.form['description']
        image = request.files.get('image')
        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            equipment.image_file = image_filename
        db.session.commit()
        flash('Sprzęt zaktualizowany.', 'success')
        return redirect(url_for('index'))
    return render_template('edit_equipment.html', equipment=equipment)

@app.route('/delete_equipment/<int:id>')
@login_required
def delete_equipment(id):
    if not current_user.is_admin:
        flash('Brak dostępu.', 'danger')
        return redirect(url_for('index'))
    equipment = Equipment.query.get_or_404(id)
    db.session.delete(equipment)
    db.session.commit()
    flash('Sprzęt usunięty.', 'success')
    return redirect(url_for('index'))

@app.route('/equipment/<int:equipment_id>', methods=['GET', 'POST'])
@login_required
def equipment_detail(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    reservation = Reservation.query.filter_by(equipment_id=equipment_id).first() if equipment.is_reserved else None

    if request.method == 'POST' and not equipment.is_reserved:
        try:
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            if end_date < start_date:
                flash('Data końca musi być po dacie początku.', 'danger')
                return redirect(url_for('equipment_detail', equipment_id=equipment_id))
            new_reservation = Reservation(user_id=current_user.id, equipment_id=equipment_id,
                                          start_date=start_date, end_date=end_date)
            equipment.is_reserved = True
            db.session.add(new_reservation)
            db.session.commit()
            flash('Zarezerwowano!', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('Niepoprawny format daty.', 'danger')
    return render_template('equipment_detail.html', equipment=equipment, reservation=reservation)

@app.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id and not current_user.is_admin:
        flash('Brak dostępu do anulowania.', 'danger')
        return redirect(url_for('index'))
    reservation.equipment.is_reserved = False
    db.session.delete(reservation)
    db.session.commit()
    flash('Rezerwacja anulowana.', 'success')
    return redirect(url_for('index'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)