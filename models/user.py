from . import db

class User(db.Model):

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"User(id={self.user_id}, name={self.user_name}, email={self.email})"

    def add_test_user():
        test_user = User(user_id=1, user_name="test user", email="test@test.com", password="password")
        db.session.add(test_user)
        db.session.commit()