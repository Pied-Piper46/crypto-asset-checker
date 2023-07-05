from . import db
from sqlalchemy import Enum
from utilities import get_all_trade_history

class TradeHistory(db.Model):

    __tablename__ = 'trade_history'

    trade_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    pair = db.Column(db.String(120), nullable=False)
    trade_type = db.Column(Enum('buy', 'sell'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def get_trade_history(user_id):

        return TradeHistory.query.filter_by(user_id=user_id).all()

    def add_new_trades():

        user_id = 1 # fixed so far
        new_trades = []
        all_trade_history = get_all_trade_history()
        for pair, trades in all_trade_history.items():
            for trade in trades:
                existing_trade = TradeHistory.query.filter_by(trade_id=trade['id']).first()

                if existing_trade is None:
                    new_trade = TradeHistory(
                        trade_id=int(trade['id']),
                        user_id=user_id,
                        timestamp=int(trade['timestamp']),
                        pair=pair, trade_type=trade['side'],
                        amount=trade['amount'],
                        price=trade['price']
                    )
                    new_trades.append(new_trade)

        db.session().add_all(new_trades)
        db.session().commit()