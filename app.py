from flask import Flask
from controllers.index import index_page
app = Flask(__name__)
app.register_blueprint(index_page, url_prefix='/')

if __name__ == "__main__":
    app.run(debug=True)