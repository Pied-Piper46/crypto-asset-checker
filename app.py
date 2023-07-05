from flask import Flask
from controllers.index import index_page
from controllers.test import test_page
from models import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.register_blueprint(index_page)
    app.register_blueprint(test_page)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)