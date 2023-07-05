from flask import Blueprint, render_template
from models.trade_history import TradeHistory
import utilities


index_page = Blueprint("index_page", __name__)

@index_page.route("/")
def index():
    user_id = 1
    trade_history = TradeHistory.get_trade_history(user_id)
    results = utilities.trade_results(trade_history)
    summary = utilities.calculate_summary(results)

    return render_template('index.html', results=results, summary=summary)