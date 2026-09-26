from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_super_segura'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(150))

# Modelo para registrar los accesos de los usuarios (Historial de logins)
class LoginLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            
            # Guardar el registro de inicio de sesión exitoso en la base de datos
            nuevo_registro = LoginLog(username=user.username)
            db.session.add(nuevo_registro)
            db.session.commit()
            
            return "¡Login Exitoso y registrado en la BD!"
            
        flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/reset-password', methods=['POST'])
def reset_password():
    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    flash('Solicitud enviada. Revisa tu correo electrónico.')
    return redirect(url_for('login'))

# Ruta para visualizar/validar los usuarios registrados en el sistema
@app.route('/usuarios')
def ver_usuarios():
    usuarios = User.query.all()
    html = "<h1>Usuarios Registrados en el Sistema</h1><ul>"
    for u in usuarios:
        html += f"<li>ID: {u.id} - Usuario: <b>{u.username}</b></li>"
    html += "</ul>"
    return html

# Ruta para visualizar los registros de inicio de sesión (Logs)
@app.route('/logs')
def ver_logs():
    registros = LoginLog.query.order_by(LoginLog.timestamp.desc()).all()
    html = "<h1>Registro de Accesos (Logins)</h1><ul>"
    for reg in registros:
        html += f"<li>Usuario: <b>{reg.username}</b> - Fecha y Hora (UTC): {reg.timestamp}</li>"
    html += "</ul>"
    return html

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
