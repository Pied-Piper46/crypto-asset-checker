from flask import Blueprint, render_template
from models import transaction, user

test_page = Blueprint("test_page", __name__)

@test_page.route("/test")
def test():
    
    # user.add_test_user()
    # transaction.add_transactions_to_db()
    transactions = transaction.get_transactions(1)

    return render_template('test.html', transactions=transactions)