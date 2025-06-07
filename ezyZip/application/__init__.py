from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_session import Session

db=SQLAlchemy()
admin=Admin()
db_name="database.db"

def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY']='dhecbchjc'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SQLALCHEMY_DATABASE_URI']=f"sqlite:///{db_name}"
    db.init_app(app)
    admin.init_app(app)
    from .auth import auth
    from .views import views
    from .donate import donate
    from .vendor import vendor
    from .donate import donate
    from .models import User,Messages,BloodStock,Vendor,Donor
    app.register_blueprint(auth,url_prefix='/')
    app.register_blueprint(views,url_prefix='/')
    app.register_blueprint(donate,url_prefix='/')
    app.register_blueprint(vendor,url_prefix='/vendor/')
    create_database(app)
    admin.add_view(ModelView(User,db.session))
    admin.add_view(ModelView(Messages,db.session))
    admin.add_view(ModelView(BloodStock,db.session))
    admin.add_view(ModelView(Vendor,db.session))
    admin.add_view(ModelView(Donor,db.session))
    
    loginmanager=LoginManager()
    loginmanager.login_view='auth.login'
    loginmanager.init_app(app)

    @loginmanager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app


def create_database(app):
    if not path.exists('website/'+db_name):
        with app.app_context():
          db.create_all()
        print('The database has been created')
    else:
        print('The database exists')


