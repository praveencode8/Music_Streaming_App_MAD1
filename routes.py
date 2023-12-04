from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Song, Playlist, Genre, Rating
from app import app
from datetime import datetime

def auth_required(func):
    @wraps(func) 
    def decorated_func(*args, **kwargs):
        if 'user_id' not in session:
            flash('Login First.')
            return redirect(url_for('landing'))
        return func(*args, **kwargs)
    return decorated_func

def admin_required(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if 'user_id' not in session:
            flash('Login First.')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user.is_admin:
            flash('You are not authorized to view this page.')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_func

def creator_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))

        user = User.query.get(user_id)
        if not user or not user.is_creator:
            flash('You need to be a creator first to access this page. Click on the Creator Account on the home page.')
            return redirect(url_for('index')) 

        return func(*args, **kwargs)
    return decorated_function

@app.route('/') 
@auth_required
def index():
    user = User.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin'))          
    else:
        songs = Song.query.all()
        playlists = Playlist.query.filter_by(user_id=user.id).all()

        genres = Genre.query.all()
        # Filter genres to only include those with songs
        songs_by_genre = {}
        for genre in genres:
            genre_songs = Song.query.filter_by(genre=genre.name).all()
            if genre_songs:
                songs_by_genre[genre.name] = genre_songs
        return render_template('index.html', user =user, songs=songs,  playlists=playlists, songs_by_genre=songs_by_genre)

@app.route('/admin')
@admin_required
def admin():
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to view this page.')
        return redirect(url_for('index'))

    normal_user_count = User.query.filter_by(is_admin=False).count()
    creator_count = User.query.filter_by(is_creator=True).count()
    total_tracks = Song.query.count()
    total_albums = len(set(song.album_name for song in Song.query.all() if song.album_name))

    return render_template('admin.html', user=user, normal_user_count=normal_user_count,
                           creator_count=creator_count, total_tracks=total_tracks, total_albums=total_albums)

@app.route('/admin/manage-tracks')
@admin_required
def manage_tracks():
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to view this page.')
        return redirect(url_for('index'))

    # Fetch all tracks
    tracks = Song.query.all()
    return render_template('manage_tracks.html', tracks=tracks)

@app.route('/admin/delete-song/<int:song_id>', methods=['POST'])
@admin_required
def admin_delete_song(song_id):
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to perform this action.')
        return redirect(url_for('index'))
    
    # # Delete related ratings first
    # Rating.query.filter_by(song_id=song_id).delete()

    song = Song.query.get(song_id)
    db.session.delete(song)
    db.session.commit()
    flash('Song deleted successfully.')
    return redirect(url_for('manage_tracks'))

@app.route('/admin/blacklist-user/<int:user_id>', methods=['POST'])
@admin_required
def blacklist_user(user_id):
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to perform this action.')
        return redirect(url_for('index'))

    user_to_blacklist = User.query.get(user_id)
    user_to_blacklist.is_blacklisted = True
    db.session.commit()
    flash('User has been blacklisted.')
    return redirect(url_for('manage_tracks'))  

@app.route('/admin/unblacklist-user/<int:user_id>', methods=['POST'])
@admin_required
def unblacklist_user(user_id):
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to perform this action.')
        return redirect(url_for('index'))

    user_to_unblacklist = User.query.get_or_404(user_id)
    user_to_unblacklist.is_blacklisted = False
    db.session.commit()
    flash('User has been removed from the blacklist.')
    return redirect(url_for('manage_tracks'))  


@app.route('/profile')
@auth_required
def profile():
    return render_template('profile.html', user=User.query.get(session['user_id']))

@app.route('/profile', methods=['POST'])
@auth_required
def profile_post():
    user = User.query.get(session['user_id'])
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')
    
    if username == '' or password == '' or cpassword == '':
        flash('Username or password can not be empty.')
        return redirect(url_for('profile'))
    if not user.check_password(cpassword):
        flash('Incorrect password')
        return redirect(url_for('profile'))
    if User.query.filter_by(username=username).first() and username != user.username:
        flash('User already exists, choose other username.')
        return redirect(url_for('profile'))
    
    user.username = username
    user.email = email
    user.password = password
    db.session.commit()
    flash('Profile updated successfully.')
    return redirect(url_for('profile'))

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/user_login')
def user_login():
    # Redirect to index if already logged in
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('user_login.html')

@app.route('/user_login', methods=['POST'])
def user_login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == '' or password == '':
        flash('Username or password can not be empty.')
        return redirect(url_for('user_login'))
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User does not exist.')
        return redirect(url_for('user_login'))
    if not user.check_password(password):
        flash('Incorrect password')
        return redirect(url_for('user_login'))
    #login success
    session['user_id'] = user.id
    return redirect(url_for('index'))

@app.route('/admin_login')
def admin_login():
    # Redirect to admin dashboard if already logged in as admin
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.is_admin:
            return redirect(url_for('admin'))
    return render_template('admin_login.html')

@app.route('/admin_login', methods=['POST'])
def admin_login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == '' or password == '':
        flash('Username or password can not be empty.')
        return redirect(url_for('admin_login'))
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User does not exist.')
        return redirect(url_for('admin_login'))
    if not user.check_password(password):
        flash('Incorrect password')
        return redirect(url_for('admin_login'))
    if not user.is_admin:
        flash('You are not authorized to view this page.')
        return redirect(url_for('admin_login'))
    #login success
    session['user_id'] = user.id
    return redirect(url_for('admin'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    password = request.form.get("password")
    email = request.form.get('email')
    if username == '' or password == '':
        flash('Username or password can not be empty.')
        return redirect(url_for('register'))
    if User.query.filter_by(username=username).first():
        flash('User already exists, choose other username.')
        return redirect(url_for('register'))
    user = User(username= username, password= password, email=email)
    db.session.add(user)
    db.session.commit()
    flash('User registered successfully.')
    return redirect(url_for('user_login'))

@app.route('/check-creator')
@auth_required
def check_creator():
    user_id = session['user_id']
    user = User.query.get(user_id)

    # Prevent admins from becoming creators
    if user.is_admin:
        flash('Admins cannot become creators.')
        return redirect(url_for('admin'))
    
    if not user.is_creator:
        flash('You are not a creator.')
        return redirect(url_for('become_creator'))
    else:
        return redirect(url_for('creator_dashboard'))

@app.route('/become-creator')
@auth_required
def become_creator():
    user_id = session['user_id']
    user = User.query.get(user_id)

    # Prevent admins from becoming creators
    if user.is_admin:
        flash('Admins cannot become creators.')
        return redirect(url_for('admin'))
    else:
        return render_template('become_creator.html')

@app.route('/confirm-creator')
@auth_required
def confirm_creator():
    user_id = session['user_id']
    user = User.query.get(user_id)
    # Prevent admins from becoming creators
    if user.is_admin:
        flash('Admins cannot become creators.')
        return redirect(url_for('admin'))
    user.is_creator = True
    db.session.commit()
    return redirect(url_for('creator_dashboard'))


@app.route('/creator-dashboard')
@creator_required
def creator_dashboard():
    user_id = session['user_id']
    user = User.query.get(user_id)
    is_creator = User.query.get(user_id).is_creator
    user_songs = Song.query.filter_by(creator_id=user_id).all()
    total_songs = len(user_songs)

    # Prevent admins from becoming creators
    if user.is_admin:
        flash('Admins cannot become creators.')
        return redirect(url_for('admin'))
    
    if not user.is_creator:
        flash('You are not a creator.')
        return redirect(url_for('become_creator'))
    # Calculate average ratings
    avg_rating = 0
    if user_songs:
        total_ratings = sum([rating.rating for song in user_songs for rating in song.ratings])
        total_rating_counts = sum([len(song.ratings) for song in user_songs])
        avg_rating = total_ratings / total_rating_counts if total_rating_counts > 0 else 0

    # Count total albums
    total_albums = len(set(song.album_name for song in user_songs if song.album_name))

    return render_template('creator.html', songs=user_songs, total_songs=total_songs, 
                           avg_rating=avg_rating, total_albums=total_albums)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('user_login'))



#----------Song Routes--------#

@app.route('/search', methods=['GET'])
def search():
    search_parameter = request.args.get('parameter')
    search_query = request.args.get('query')

    # Perform search based on the parameter
    if search_parameter == 'song':
        results = Song.query.filter(Song.name.ilike(f'%{search_query}%')).all()
        result_type = 'Songs'
    elif search_parameter == 'artist':
        results = Song.query.filter(Song.artist_name.ilike(f'%{search_query}%')).all()
        result_type = 'Artists'
    elif search_parameter == 'album':
        results = Song.query.filter(Song.album_name.ilike(f'%{search_query}%')).all()
        result_type = 'Albums'
    elif search_parameter == 'genre':
        results = Song.query.filter(Song.genre.ilike(f'%{search_query}%')).all()
        result_type = 'Genres'
    elif search_parameter == 'rating':
        try:
            rating_query = float(search_query)
            results = Song.query.filter(Song.average_rating == rating_query).all()
            result_type = 'Ratings'
        except ValueError:
            flash("Invalid rating value")
            return redirect(url_for('index'))
    else:
        results = []
        result_type = 'Unknown'

    return render_template('search_results.html', results=results, result_type=result_type)


@app.route('/playlist/<int:id>')
@auth_required
def view_playlist(id):
    user_id = session['user_id']
    playlist = Playlist.query.get(id)

    # Check if the current user owns the playlist
    if playlist.user_id != user_id:
        flash('You do not have permission to view this playlist.')
        return redirect(url_for('index'))  

    return render_template('playlist/view_playlist.html', playlist=playlist)

@app.route('/playlist/delete/<int:id>', methods=['POST'])
@auth_required
def delete_playlist(id):
    user_id = session['user_id']
    playlist = Playlist.query.get(id)

    # Check if the current user owns the playlist
    if playlist.user_id != user_id:
        flash('You do not have permission to delete this playlist.')
        return redirect(url_for('index'))

    db.session.delete(playlist)
    db.session.commit()
    flash('Playlist deleted successfully.')
    return redirect(url_for('index'))  


@app.route('/playlist/create')
@auth_required
def create_playlist():
    user = User.query.get(session['user_id'])
    # Render a form to create a new playlist
    return render_template('playlist/create_playlist.html', user = user , songs=Song.query.all())

@app.route('/playlist/create', methods=['POST'])
@auth_required
def create_playlist_post():
    playlist_name = request.form.get('playlist_name')
    selected_song_ids = request.form.getlist('songs')  

    if not playlist_name:
        flash('Playlist name is required.')
        return redirect(url_for('create_playlist'))

    new_playlist = Playlist(name=playlist_name, user_id=session['user_id'])
    db.session.add(new_playlist)
    db.session.flush()  # Flush to get the new_playlist id

    # Add selected songs to the playlist
    for song_id in selected_song_ids:
        song = Song.query.get(song_id)
        if song:
            # Assuming you have a relationship or a way to associate songs with a playlist
            new_playlist.songs.append(song)

    db.session.commit()
    flash('Playlist created successfully.')
    return redirect(url_for('index'))

@app.route('/song/<int:song_id>/rate', methods=['POST'])
@auth_required
def rate_song(song_id):
    user_id = session['user_id']
    user = User.query.get(user_id)
    rating_value = request.form.get('rating')  # Assuming rating is passed as a form data

    # Prevent admins from rating songs
    if user.is_admin:
        flash('Admins cannot rate songs.')
        return redirect(url_for('admin'))

    # Get the song to check its creator
    song = Song.query.get(song_id)
    if not song:
        flash('Song not found.')
        return redirect(url_for('index'))

    # Prevent the creator of the song from rating their own song
    if user_id == song.creator_id:
        flash('Creators cannot rate their own songs.')
        return redirect(url_for('index'))
    
    if not rating_value:
        flash('Rating is required.')
        return redirect(url_for('view_lyrics', id=song_id))

    rating_value = float(request.form.get('rating'))
    song = Song.query.get(song_id)

    # Add or update the rating
    existing_rating = Rating.query.filter_by(song_id=song_id, user_id=user_id).first()
    if existing_rating:
        existing_rating.rating = rating_value
    else:
        new_rating = Rating(song_id=song_id, user_id=user_id, rating=rating_value)
        db.session.add(new_rating)

    # Recalculate the average rating
    total_ratings = sum([rating.rating for rating in song.ratings]) + rating_value
    song.average_rating = total_ratings / (len(song.ratings) + 1 if not existing_rating else len(song.ratings))
    db.session.commit()

    flash('Rating submitted successfully.')
    return redirect(url_for('view_lyrics', id=song_id))


@app.route('/song/upload')
@creator_required
def upload_song():
    genres = Genre.query.all()
    user_id = session['user_id']

    # Fetch distinct album names created by the user
    albums = Song.query.filter(Song.creator_id == user_id).with_entities(Song.album_name).distinct().all()
    
    return render_template('song/upload.html', user=User.query.get(user_id), 
                           nowstring=datetime.now().strftime('%Y-%m-%d'), albums=albums, genres=genres)


@app.route('/song/upload', methods=['POST'])
@creator_required
def upload_song_post():
    name = request.form.get('name')
    genre = request.form.get('genre')
    lyrics = request.form.get('lyrics')
    artist_name = request.form.get('artist_name')
    release_date_str = request.form.get('release_date')
    file = request.files.get('file')
    album_name = request.form.get('album_name')

    
    if name == '' or genre == '' or lyrics == '' or album_name =='' or artist_name == '' or release_date_str == '' :
        flash('All fields are required.')
        return redirect(url_for('upload_song_post'))
    
    
    # Convert release_date from string to date object
    release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()

    song = Song(name=name, genre=genre, lyrics=lyrics, 
                release_date=release_date, artist_name=artist_name, 
                album_name=album_name, creator_id=session['user_id'])
    db.session.add(song)
    db.session.commit()
    flash('Song uploaded successfully.')
    return redirect(url_for('creator_dashboard'))

@app.route('/song/<int:id>/lyrics')
@auth_required
def view_lyrics(id):
    song = Song.query.get(id)
    
    if not song:
        flash("Song not found.")
        return redirect(url_for('index'))
    average_rating = song.average_rating if song.average_rating else "Not rated yet"
    return render_template('song/view_lyrics.html', song=song, average_rating=average_rating)


@app.route('/song/<int:id>/edit')
@creator_required
def edit_song(id):
    song = Song.query.get(id)
    genres = Genre.query.all()
    return render_template('song/edit_song.html', song=song, genres=genres) 

@app.route('/song/<int:id>/edit', methods=['POST'])
@creator_required
def update_song(id):
    song = Song.query.get_or_404(id)
    if song.creator_id != session['user_id']:
        flash('You are not authorized to edit this song.')
        return redirect(url_for('creator_dashboard'))

    song.name = request.form['name']
    song.genre = request.form['genre']
    song.lyrics = request.form['lyrics']
    song.artist_name = request.form['artist_name']
    song.album_name = request.form['album_name']
    song.release_date = datetime.strptime(request.form['release_date'], '%Y-%m-%d').date()
    db.session.commit()
    flash('Song updated successfully.')
    return redirect(url_for('creator_dashboard'))

@app.route('/song/<int:id>/confirm-delete')
@creator_required
def confirm_delete_song(id):
    song = Song.query.get(id)
    if song.creator_id != session['user_id']:
        flash('You are not authorized to view this page.')
        return redirect(url_for('creator'))
    return render_template('song/confirm_delete.html', song=song)

@app.route('/song/<int:id>/delete', methods=['POST'])
@creator_required
def creator_delete_song(id):
    song = Song.query.get(id)
    if song.creator_id != session['user_id']:
        flash('You are not authorized to delete this song.')
        return redirect(url_for('creator_dashboard'))
    db.session.delete(song)
    db.session.commit()
    flash('Song deleted successfully.')
    return redirect(url_for('creator_dashboard'))