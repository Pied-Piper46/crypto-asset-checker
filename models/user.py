from . import db

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

def add_test_user():
    test_user = User(user_id=1, user_name="test user", email="test@test.com", password="password")
    db.session.add(test_user)
    db.session.commit()