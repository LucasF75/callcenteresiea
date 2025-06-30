Readlist - Book Tracking Application
Overview

Readlist is a web application designed to help book lovers track their reading, discover new books, and interact with a community of readers. The application provides personalized book recommendations based on your reading history and preferences.
Features

    User Authentication: Secure login and registration system

    Book Management: Save, like, and track books you've read

    Personalized Recommendations: Get book suggestions based on your preferences

    Book Search: Search for books using the Google Books API

    Community Features: Leave comments on books and see what others are reading

    Reading History: Track recently viewed books

    Theme Switching: Toggle between light and dark themes

    Responsive Design: Works on both desktop and mobile devices

Technologies Used
Backend

    Python

    Flask (web framework)

    Flask-SQLAlchemy (ORM)

    Flask-Login (authentication)

    Flask-Migrate (database migrations)

    MySQL (database)

Frontend

    HTML5

    CSS3

    JavaScript (for dynamic features)

Infrastructure

    Docker (containerization)

    Docker Compose (orchestration)

Installation
Prerequisites

    Docker

    Docker Compose

Setup Instructions

    Clone the repository:
    bash

git clone [repository-url]
cd readlist

Build and start the containers:
bash

docker-compose up --build

Initialize the database (in a new terminal):
bash

    docker-compose exec web python init_db.py

    The application will be available at: http://localhost:5000

Usage
Default Admin Account

    Email: admin@readlist.com

    Password: admin123

Regular User

    Register a new account or use the admin credentials to log in

Project Structure
text

readlist/
├── app/                      # Application code
│   ├── __init__.py           # Flask application factory
│   ├── auth.py               # Authentication routes
│   ├── forms.py              # WTForms definitions
│   ├── models.py             # Database models
│   ├── routes.py             # Main application routes
│   └── templates/            # HTML templates
├── static/                   # Static files
│   └── css/                  # CSS stylesheets
│       ├── bliblio.css
│       ├── details.css
│       ├── home.css
│       ├── login.css
│       ├── main.css
│       ├── profile.css
│       └── signup.css
├── docker-compose.yml        # Docker configuration
├── init_db.py                # Database initialization script
├── requirements.txt          # Python dependencies
└── run.py                    # Application entry point

API Integration

The application integrates with the Google Books API to:

    Search for books

    Retrieve book details

    Get cover images
