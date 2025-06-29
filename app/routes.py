from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session, Flask
from flask_login import login_required, current_user
from datetime import datetime
from app.models import SavedBook, Comment, BookLike, RecentlyViewed
from app import db
import requests
import random

main = Blueprint('main', __name__)
    

@main.route('/switch_theme')
def switch_theme():
    current_theme = session.get('theme', 'dark')
    session['theme'] = 'light' if current_theme == 'dark' else 'dark'
    return redirect(request.referrer or url_for('main.home'))

@main.route('/')
@login_required  # Pour que seul un utilisateur connecté y ait accès
def home():
    # Recommandations générales (déjà faites, ici juste en rappel)
    recommended_books = []  
    # Par défaut thème sombre
    theme = session.get('theme', 'dark')

    # --- Recommandations basées sur les likes ---
    liked_books = BookLike.query.filter_by(user_id=current_user.id, liked=True).all()

    genres_count = {}

    for liked in liked_books:
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes/{liked.book_id}')
        if response.status_code == 200:
            data = response.json()
            volume_info = data.get('volumeInfo', {})
            categories = volume_info.get('categories', [])
            for category in categories:
                genres_count[category] = genres_count.get(category, 0) + 1

    recommendations = []
    if genres_count:
        top_genre = max(genres_count, key=genres_count.get)
        url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{top_genre}&maxResults=6'
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get('items', []):
                vi = item.get('volumeInfo', {})
                recommendations.append({
                    'id': item.get('id'),
                    'title': vi.get('title'),
                    'authors': vi.get('authors', []),
                    'thumbnail': vi.get('imageLinks', {}).get('thumbnail')
                })

    # Livres récemment consultés
    recent_books_raw = RecentlyViewed.query.filter_by(user_id=current_user.id)\
                            .order_by(RecentlyViewed.timestamp.desc()).limit(6).all()

    recent_books = []
    for recent in recent_books_raw:
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes/{recent.book_id}')
        if response.status_code == 200:
            data = response.json()
            volume_info = data.get('volumeInfo', {})
            recent_books.append({
                'id': recent.book_id,
                'title': volume_info.get('title'),
                'authors': volume_info.get('authors', []),
                'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail')
            })


    quotes = [
    "Lire, c'est rêver les yeux ouverts.",
    "Un livre est un rêve que vous tenez entre vos mains.",
    "Les livres sont des miroirs : on y voit que ce qu’on y porte.",
    "Un lecteur vit mille vies avant de mourir.",
    "Lire, c’est aller à la rencontre d’une chose qui va exister."
]

    random_quote = random.choice(quotes)

    return render_template('home.html', theme=theme, user=current_user, recommended_books=recommended_books, recommendations=recommendations, random_quote=random_quote, recent_books=recent_books)

@main.route('/search', methods=['GET', 'POST'])
def search():
    theme = session.get('theme', 'dark')
    books = []
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            url = f'https://www.googleapis.com/books/v1/volumes?q={query}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    volume_info = item.get('volumeInfo', {})
                    books.append({
                        'id': item.get('id'),
                        'title': volume_info.get('title'),
                        'authors': volume_info.get('authors', []),
                        'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail')
                    })
    return render_template('search.html', books=books, theme=theme)



@main.route('/book/<book_id>')
@login_required
def book_detail(book_id):
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes/{book_id}")
    if response.status_code == 200:
        data = response.json()
        volume_info = data.get('volumeInfo', {})
        comments = Comment.query.filter_by(book_id=book_id).order_by(Comment.timestamp.desc()).all()

        # Enregistrement dans l'historique
        viewed = RecentlyViewed.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        if viewed:
            viewed.timestamp = datetime.utcnow()  # mise à jour si déjà vu
        else:
            new_view = RecentlyViewed(user_id=current_user.id, book_id=book_id)
            db.session.add(new_view)
        db.session.commit()

        book = {
            'id': book_id,
            'title': volume_info.get('title'),
            'authors': volume_info.get('authors', []),
            'description': volume_info.get('description'),
            'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail')
        }

        is_saved = SavedBook.query.filter_by(user_id=current_user.id, book_id=book_id).first() is not None
        liked = BookLike.query.filter_by(user_id=current_user.id, book_id=book_id, liked=True).first() is not None
        theme = session.get('theme', 'dark')
        return render_template('details.html', book=book, is_saved=is_saved, comments=comments, liked=liked, theme=theme)

    flash("Livre introuvable.")
    return redirect(url_for('main.search'))



@main.route('/save-book/<book_id>', methods=['POST'])
@login_required
def save_book(book_id):
    action = request.form.get('action')

    if action == 'save':
        if not SavedBook.query.filter_by(user_id=current_user.id, book_id=book_id).first():
            new_book = SavedBook(user_id=current_user.id, book_id=book_id)
            db.session.add(new_book)
            db.session.commit()
            flash('Livre enregistré.')
    elif action == 'delete':
        saved = SavedBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        if saved:
            db.session.delete(saved)
            db.session.commit()
            flash('Livre supprimé.')

    # Redirige vers la page d'où vient la requête (ex : liste enregistrés, détails, etc.)
    return redirect(request.referrer or url_for('main.book_detail', book_id=book_id))


@main.route('/saved')
@login_required
def saved_books():
    saved = SavedBook.query.filter_by(user_id=current_user.id).all()
    books = []
    theme = session.get('theme', 'dark')

    for item in saved:
        response = requests.get(f"https://www.googleapis.com/books/v1/volumes/{item.book_id}")
        if response.status_code == 200:
            data = response.json()
            volume_info = data.get('volumeInfo', {})
            books.append({
                'id': item.book_id,
                'title': volume_info.get('title'),
                'authors': volume_info.get('authors', []),
                'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail')
            })

    return render_template('saved.html', books=books, theme=theme)



@main.route('/like-book/<book_id>', methods=['POST'])
@login_required
def like_book(book_id):
    action = request.form.get('action')
    like_entry = BookLike.query.filter_by(user_id=current_user.id, book_id=book_id).first()

    if action == 'like':
        if not like_entry:
            like_entry = BookLike(user_id=current_user.id, book_id=book_id, liked=True)
            db.session.add(like_entry)
        else:
            like_entry.liked = True
        db.session.commit()
        flash("Livre aimé !")

    elif action == 'unlike':
        if like_entry:
            db.session.delete(like_entry)
            db.session.commit()
            flash("Like supprimé.")

    # Redirige toujours vers la page précédente (d'où vient le formulaire)
    return redirect(request.referrer or url_for('main.liked_books'))



@main.route('/liked')
@login_required
def liked_books():
    liked = BookLike.query.filter_by(user_id=current_user.id, liked=True).all()
    books = []

    for entry in liked:
        response = requests.get(f"https://www.googleapis.com/books/v1/volumes/{entry.book_id}")
        theme = session.get('theme', 'dark')
        if response.status_code == 200:
            data = response.json()
            volume_info = data.get('volumeInfo', {})
            books.append({
                'id': entry.book_id,
                'title': volume_info.get('title', 'Titre inconnu'),
                'authors': volume_info.get('authors', []),
                'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail')
            })

    return render_template('liked.html', books=books, theme=theme)




@main.route('/book/<book_id>/comment', methods=['POST'])
@login_required
def comment_book(book_id):
    content = request.form.get('comment')
    if content:
        new_comment = Comment(book_id=book_id, user_id=current_user.id, content=content)
        db.session.add(new_comment)
        db.session.commit()
        flash('Commentaire ajouté.')
    return redirect(url_for('main.book_detail', book_id=book_id))


@main.route('/profile')
@login_required
def profile():
    
    theme = session.get('theme', 'dark')
    user_comments = Comment.query.filter_by(user_id=current_user.id).all()

    return render_template('profile.html', user=current_user, comments=user_comments, theme=theme)


@main.route('/search-by-genre', methods=['POST'])
@login_required
def search_by_genre():
    genre = request.form.get('genre')
    books = []

    if genre:
        url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{genre}&maxResults=10'
        response = requests.get(url)
        theme = session.get('theme', 'dark')
        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                volume_info = item.get('volumeInfo', {})
                books.append({
                    'id': item.get('id'),
                    'title': volume_info.get('title'),
                    'authors': volume_info.get('authors', []),
                    'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail')
                })

    return render_template('genre.html', books=books, genre=genre, theme=theme)


@main.route('/api/recent-books')
@login_required
def api_recent_books():
    recent_books_raw = RecentlyViewed.query.filter_by(user_id=current_user.id) \
                        .order_by(RecentlyViewed.timestamp.desc()).limit(6).all()

    recent_books = []
    for recent in recent_books_raw:
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes/{recent.book_id}')
        if response.status_code == 200:
            data = response.json()
            volume_info = data.get('volumeInfo', {})
            recent_books.append({
                'id': recent.book_id,
                'title': volume_info.get('title'),
                'authors': volume_info.get('authors', []),
                'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail')
            })

    return jsonify(recent_books)


@main.route('/delete_comment/<int:comment_id>/<string:book_id>', methods=['POST'])
@login_required
def delete_comment(comment_id, book_id):
    if not current_user.is_admin:
        flash("Action réservée à l'administrateur.")
        return redirect(url_for('main.book_detail', book_id=book_id))

    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash("Commentaire supprimé avec succès.")
    return redirect(url_for('main.book_detail', book_id=book_id))