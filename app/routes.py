from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
import requests

from app.models import SavedBook
from app import db

main = Blueprint('main', __name__)

@main.route('/')
@login_required  # Pour que seul un utilisateur connecté y ait accès
def home():
    return render_template('home.html', user=current_user)

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

        book = {
            'id': book_id,
            'title': volume_info.get('title'),
            'authors': volume_info.get('authors', []),
            'description': volume_info.get('description'),
            'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail')
        }

        is_saved = SavedBook.query.filter_by(user_id=current_user.id, book_id=book_id).first() is not None

        return render_template('details.html', book=book, is_saved=is_saved)


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
