from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
import requests


from app.models import SavedBook, Comment, BookLike

from app import db

main = Blueprint('main', __name__)

@main.route('/')
@login_required  # Pour que seul un utilisateur connecté y ait accès
def home():
    # Recommandations générales (déjà faites, ici juste en rappel)
    recommended_books = []  
    # ... ton code pour remplir recommended_books ...

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
        url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{top_genre}&maxResults=5'
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

    return render_template('home.html', user=current_user, recommended_books=recommended_books, recommendations=recommendations)

@main.route('/search', methods=['GET', 'POST'])
def search():
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
    return render_template('search.html', books=books)



@main.route('/book/<book_id>')
@login_required
def book_detail(book_id):
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes/{book_id}")
    if response.status_code == 200:
        data = response.json()
        volume_info = data.get('volumeInfo', {})
        comments = Comment.query.filter_by(book_id=book_id).order_by(Comment.timestamp.desc()).all()

        book = {
            'id': book_id,
            'title': volume_info.get('title'),
            'authors': volume_info.get('authors', []),
            'description': volume_info.get('description'),
            'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail')
        }

        is_saved = SavedBook.query.filter_by(user_id=current_user.id, book_id=book_id).first() is not None
        liked = BookLike.query.filter_by(user_id=current_user.id, book_id=book_id, liked=True).first() is not None

        return render_template('details.html', book=book, is_saved=is_saved, comments=comments, liked=liked)


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

    return redirect(url_for('main.book_detail', book_id=book_id))


@main.route('/saved')
@login_required
def saved_books():
    saved = SavedBook.query.filter_by(user_id=current_user.id).all()
    books = []

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

    return render_template('saved.html', books=books)


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
    return redirect(url_for('main.book_detail', book_id=book_id))



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
    saved_books_raw = SavedBook.query.filter_by(user_id=current_user.id).all()
    saved_books = []

    for saved in saved_books_raw:
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes/{saved.book_id}')
        if response.status_code == 200:
            data = response.json()
            volume_info = data.get('volumeInfo', {})
            saved_books.append({
                'id': saved.book_id,
                'title': volume_info.get('title', 'Titre inconnu'),
                'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail')
            })

    user_comments = Comment.query.filter_by(user_id=current_user.id).all()

    return render_template('profile.html', user=current_user, saved_books=saved_books, comments=user_comments)
