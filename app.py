import utilities
from flask import Flask, render_template
app = Flask(__name__)

pair = 'BTC/JPY'

@app.route('/')
def home():
    results = utilities.all_pairs_results()

    return render_template('index.html', results=results)

if __name__ == "__main__":
    app.run(debug=True)
