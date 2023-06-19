import utilities
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    results = utilities.all_pairs_results()
    summary = utilities.calculate_summary(results)

    return render_template('index.html', results=results, summary=summary)

if __name__ == "__main__":
    app.run(debug=True)
