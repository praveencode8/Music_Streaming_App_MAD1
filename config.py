from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"

app.secret_key = "secret_key"




