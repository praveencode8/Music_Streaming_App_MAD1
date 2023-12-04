from flask_sqlalchemy import SQLAlchemy
from app import app
from werkzeug.security import generate_password_hash, check_password_hash 

db = SQLAlchemy(app)

##models
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(32), unique=True, nullable =False) 
    passhash = db.Column(db.String(512), nullable= False)
    email = db.Column(db.String(100), unique=True, nullable= False)
    is_admin = db.Column(db.Boolean, nullable= False, default =False) 
    is_creator = db.Column(db.Boolean, nullable= False, default =False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not readable')
    
    @password.setter
    def password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password) 
    
# Association table for the many-to-many relationship
playlist_songs = db.Table('playlist_songs',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True)
)

class Song(db.Model):
    __tablename__ = 'song'
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(32), unique=True, nullable =False) 
    genre = db.Column(db.String(32), db.ForeignKey('genre.name'), nullable= False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable= True)
    artist_name = db.Column(db.String(32), unique=False, nullable =False)
    album_name = db.Column(db.String(32), unique=False, nullable =False)
    lyrics = db.Column(db.String(10000), unique=True, nullable =True) 
    release_date = db.Column(db.Date, nullable= False)    
    average_rating = db.Column(db.Float, default=0)

    #realtionship to user
    creator = db.relationship('User', backref=db.backref('songs' , lazy=True))
    playlists = db.relationship('Playlist', secondary=playlist_songs, back_populates='songs')


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(32), unique=True, nullable =False) 
    
    #relationship to song
    songs = db.relationship('Song', backref=db.backref('genres' , lazy=True))

#Adding predefined genres
def add_genres():
    genres = ['Classical music', 'Folk music', 'Fusion of classical and folk music', 'Modern music', 'Rock & Roll', 'Jazz', 'Rap']
    for genre_name in genres:
        if not Genre.query.filter_by(name=genre_name).first():
            new_genre = Genre(name=genre_name)
            db.session.add(new_genre)
    db.session.commit()

class Playlist(db.Model):
    __tablename__ = 'playlist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    songs = db.relationship('Song', secondary=playlist_songs, back_populates='playlists')

class Rating(db.Model):
    __tablename__ = 'rating'
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)

    song = db.relationship('Song', backref='ratings')
    user = db.relationship('User', backref='ratings')


with app.app_context():
    db.create_all()
    #crete admin if not exists
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(username= 'admin', password= 'admin',email = 'admin@admin.com', is_admin=True)
        db.session.add(admin)
        db.session.commit()
