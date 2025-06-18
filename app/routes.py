from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
import requests

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
                books = data.get('items', [])
    return render_template('search.html', books=books)