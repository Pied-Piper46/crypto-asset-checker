from flask import Blueprint, render_template
from models import user, trade_history, deposit_history, withdrawal_history

test_page = Blueprint("test_page", __name__)

@test_page.route("/test")
def test():
    
    # user.User.add_test_user()
    withdrawal_history.WithdrawalHistory.add_new_withdrawals()
    withdrawals = withdrawal_history.WithdrawalHistory.get_withdrawal_history(1)

    return render_template('test.html', withdrawals=withdrawals)