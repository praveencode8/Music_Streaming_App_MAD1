from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

import config

from models import *
with app.app_context():
    add_genres()

def create_predefined_users():
    # List of predefined users
    predefined_users = [
        {'username': 'user1', 'password': 'user1', 'email': 'user1@email.com'},
        {'username': 'user2', 'password': 'user2', 'email': 'user2@email.com'},
        {'username': 'user3', 'password': 'user3', 'email': 'user3@email.com'},
        {'username': 'user4', 'password': 'user4', 'email': 'user4@email.com'}
    ]

    with app.app_context():
        # Check if users already exist to avoid duplication
        existing_usernames = [user.username for user in User.query.all()]
        for user_data in predefined_users:
            if user_data['username'] not in existing_usernames:
                new_user = User(
                    username=user_data['username'],
                    email=user_data['email']
                )
                new_user.password = user_data['password']  
                db.session.add(new_user)
        
        db.session.commit()

# Call the function to create users
create_predefined_users()

import routes




