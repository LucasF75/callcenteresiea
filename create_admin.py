from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash


app = create_app()  # on crée l'instance Flask depuis factory

with app.app_context():
    admin = User(
        name="Admin",
        email="admin@readlist.com",
        password=generate_password_hash("admin123", method="pbkdf2:sha256"),
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin créé avec succès.")

