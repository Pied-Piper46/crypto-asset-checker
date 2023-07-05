from flask import Blueprint, render_template
from models import trade_history, user

test_page = Blueprint("test_page", __name__)

@test_page.route("/test")
def test():
    
    # user.User.add_test_user()
    # trade_history.TradeHistory.add_new_trades()
    transactions = trade_history.TradeHistory.get_trade_history(1)

    return render_template('test.html', transactions=transactions)