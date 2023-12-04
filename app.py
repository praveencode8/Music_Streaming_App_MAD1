from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

import models
import routes

with app.app_context():
    db.create_all()
    models.add_genres()
    models.add_users()
    models.create_admin_if_not_exists()




