from flask import Blueprint, render_template
import utilities

index_page = Blueprint("index_page", __name__)

@index_page.route("/")
def index():
    results = utilities.all_pairs_results()
    summary = utilities.calculate_summary(results)

    return render_template('index.html', results=results, summary=summary)