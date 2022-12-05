from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import pathlib




db = SQLAlchemy()
DB_NAME = "database.db"



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'alexsoyoye'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    
    db.init_app(app) 

    


    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    

    from .models import User

    with app.app_context():
        db.create_all()
        excel_file_path = pathlib.Path('Line Managers.xlsx')
        lm = pd.read_excel(excel_file_path)
        lm_username=lm['username']
        lm_email=lm['email']
        lm_name=lm['full name']
        lm_location=lm['location']
        lm_password=lm['password']
        lm_department=lm['department']
        lm_status=lm['line manager status']
        lm_head=lm['head status']
        row=0

        while row < len(lm_username)-1:
            user = User.query.filter_by(username=lm_username[row]).first()
            if user:
                row=row + 1
            else:
                new_user= User(email=lm_email[row], username=lm_username[row], staff_name=lm_name[row], password=generate_password_hash(lm_password[row],method='sha256'),
                department=lm_department[row], location=lm_location[row], linemanager_status=lm_status[row],head_status=lm_head[row])
                db.session.add(new_user)
                db.session.commit()

                row=row + 1
                






   

   

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app






