from flask import Flask
from controllers.index import index_page
from controllers.test import test_page
from controllers.update_data import update_page
from models import db
from config import DATABASE_URL

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.register_blueprint(index_page)
    app.register_blueprint(test_page)
    app.register_blueprint(update_page)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)