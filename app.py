from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
# Usa una clave fuerte y cámbiala
app.config['SECRET_KEY'] = 'clave_secreta_super_segura' 
# La base de datos se guardará en la misma carpeta
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(150))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return "¡Login Exitoso!"
    return render_template('login.html')

# Esto es lo que busca Azure para iniciar la app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()