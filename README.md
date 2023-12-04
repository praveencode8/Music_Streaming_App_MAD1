# Music Streaming Application

## Description
This project involves the development of a comprehensive music streaming application, tailored to manage a wide variety of musical content including songs, albums, and playlists. It features a user-friendly interface for different user roles such as administrators, creators, and regular users, each with distinct functionalities like song uploads, playlist creation, and content management. The application also integrates rating systems, search capabilities, and user management, enhancing the overall music streaming and sharing experience.

## Technologies Used
- **Flask**: A lightweight and flexible Python web framework used for building the application's backend. It handles routing, requests, and server-side logic.
- **SQLAlchemy**: An Object-Relational Mapping (ORM) library for Python, used in conjunction with Flask. It provides an efficient way to interact with the application's database by mapping Python classes to database tables.
- **SQLite**: A lightweight, file-based database management system used for storing and managing all the application data, including user information, song details, playlists, ratings, etc.
- **HTML/CSS**: Used for structuring and styling the front-end of the application. HTML is used to define the structure of web pages, while CSS is used to style and layout these pages.
- **Jinja2 Templating Engine**: Integrated with Flask, it is used for rendering dynamic HTML content on the web pages.
- **Bootstrap**: A front-end framework used to design responsive and mobile-first web pages.
- **IDE**: Visual Studio Code

## Database Schema Design
The database consists of the following tables:
- **User**: Stores information about users of the application.
- **Song**: Holds details about each song available on the platform.
- **Genre**: Contains different music genres.
- **Playlist**: Manages user-created playlists.
- **Rating**: Stores ratings given by users to songs.
- **Playlist_Songs**: Facilitates the many-to-many relationship between Playlist and Song tables.

## ER Diagram of Database
![Untitled (1)](https://github.com/praveencode8/music_streaming/assets/72277324/d5cc28c7-5557-46bc-a6ad-5bc21a2c413c)


## Architecture and Features
### Architecture
The Music Streaming Application follows the Model-View-Controller (MVC) architecture:

1. **Model**: Handles data and business logic.
2. **View**: Presents data to the user in an interactive format.
3. **Controller**: Processes user inputs and communicates between the model and view components.

### Features
- **User Authentication and Roles**: Secure system with different user roles.
- **Music Management**: Search, playlist creation, and song management capabilities.
- **Rating System**: Users can rate songs and view average ratings.
- **Admin-Specific Features**: Manage users, songs, and albums.
- **Responsive UI**: A user-friendly interface that adapts to different screen sizes.
- **Lyrics Viewing**: View song lyrics along with rating options.

## Presentation Video Link
[https://drive.google.com/drive/folders/1IeonIIpm9eEBGj38zMmDFVB0Sp2Bw3Bz?usp=sharing](https://drive.google.com/drive/folders/1IeonIIpm9eEBGj38zMmDFVB0Sp2Bw3Bz?usp=sharing)
