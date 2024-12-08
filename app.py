from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import time
import threading

app = Flask(__name__)

# Konfigurasi database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey'  # Ganti dengan kunci rahasia yang lebih aman
db = SQLAlchemy(app)

# Konfigurasi LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Fungsi user_loader untuk Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Model untuk pengguna
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Model untuk jadwal
class Jadwal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    waktu = db.Column(db.String(5), nullable=False)  # Format HH:MM
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    user = db.relationship('User', backref=db.backref('jadwals', passive_deletes=True))

# Fungsi pengecekan waktu dan pengingat
def pengecek_waktu():
    while True:
        current_time = datetime.now().strftime("%H:%M")
        jadwals = Jadwal.query.all()
        for jadwal in jadwals:
            if jadwal.waktu == current_time:
                # Pemberitahuan di sini (email atau notifikasi web)
                print(f"Pengingat: {jadwal.judul} pada {jadwal.waktu}")
                # Kirim email atau push notification di sini
        time.sleep(60)  # Mengecek setiap menit

@app.route('/')
@login_required
def index():
    jadwals = Jadwal.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', jadwals=jadwals)

@app.route('/add', methods=['POST'])
@login_required
def add_jadwal():
    judul = request.form['judul']
    waktu = request.form['waktu']
    if judul and waktu:
        new_jadwal = Jadwal(judul=judul, waktu=waktu, user_id=current_user.id)
        db.session.add(new_jadwal)
        db.session.commit()
        flash('Jadwal berhasil ditambahkan!', 'success')
    else:
        flash('Harap masukkan judul dan waktu!', 'danger')
    return redirect(url_for('index'))

@app.route('/delete/<int:jadwal_id>', methods=['POST'])
@login_required
def delete_jadwal(jadwal_id):
    jadwal = Jadwal.query.get_or_404(jadwal_id)
    if jadwal.user_id == current_user.id:
        db.session.delete(jadwal)
        db.session.commit()
        flash('Jadwal berhasil dihapus!', 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login gagal! Cek username dan password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    with app.app_context():  # Membuat aplikasi konteks
        db.create_all()  # Membuat tabel-tabel di database
    threading.Thread(target=pengecek_waktu, daemon=True).start()  # Menjalankan pengecekan waktu
    app.run(debug=True)
