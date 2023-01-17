# FICHIER DE CONFIGURATION QUI PERMET D'APPELER TOUS LES SOUS MODULES
# POUR LE BON FONCTIONNEMENT DU PROJET
# C'EST LE DEUXIEME FICHIER QUI EST APPELER
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO

db = SQLAlchemy()
async_mode = None
socketio = SocketIO(manage_session=False)
session = Session()

def create_app(debug=False):
    # VARIABLES DENVIRONNEMENTS DE FLASK
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tchat.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SESSION_TYPE'] = 'filesystem'
    ####

    db.init_app(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from . import models

    with app.app_context():
        db.create_all()

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    session.init_app(app)
    socketio.init_app(app)
    app.run(ssl_context=('Certificates/ca.crt', 'Certificates/ca.key'))
    return app
