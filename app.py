import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ['FLASH_SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flash.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

if __name__ == '__main__':

	from views import *
	from login import *

	app.run(debug=True, host='0.0.0.0')


