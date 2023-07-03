from . import db
from sqlalchemy import Enum
from utilities import get_all_trade_history

class Transaction(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    pair = db.Column(db.String(120), nullable=False)
    transaction_type = db.Column(Enum('buy', 'sell'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)

def add_transactions_to_db():

    transactions = []
    user_id = 1
    all_trade_history = get_all_trade_history()
    for pair, trade_history in all_trade_history.items():
        new_transactions = [Transaction(transaction_id=int(data['id']), user_id=user_id, timestamp=int(data['timestamp']), pair=pair, transaction_type=data['side'], amount=data['amount'], price=data['price']) for data in trade_history]
        transactions.extend(new_transactions)

    db.session().add_all(transactions)
    db.session().commit()

def get_transactions(user_id):

    return Transaction.query.filter_by(user_id=user_id).all()