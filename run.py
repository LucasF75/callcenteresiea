from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
from flask_migrate import upgrade

app = create_app()

def create_admin():
    if not User.query.filter_by(email="admin@readlist.com").first():
        admin = User(
            email="admin@readlist.com",
            password=generate_password_hash("admin123", method='pbkdf2:sha256'),
            name="Admin",
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created.")
    else:
        print("Admin already exists.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database initialized.")
        print("Tables created with success !")
        create_admin()  # ✅ Admin creation if not exists
    app.run(debug=True, host='0.0.0.0', port=5000)