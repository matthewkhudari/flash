from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flash.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

if __name__ == '__main__':

	from views import *
	from login import *

	app.run(debug=True)

