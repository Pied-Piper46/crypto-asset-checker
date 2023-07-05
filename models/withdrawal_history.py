from . import db
from utilities import get_all_withdrawal_history

class WithdrawalHistory(db.Model):

    __tablename__ = 'withdrawal_history'

    withdrawal_id = db.Column(db.String(120), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    symbol = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def get_withdrawal_history(user_id):
        return WithdrawalHistory.query.filter_by(user_id=user_id).all()

    def add_new_withdrawals():

        user_id = 1 # fixed so far
        new_withdrawals = []
        all_withdrawal_history = get_all_withdrawal_history()

        for symbol, withdrawals in all_withdrawal_history.items():
            for withdrawal in withdrawals:
                existing_withdrawal = WithdrawalHistory.query.filter_by(withdrawal_id=withdrawal['uuid']).first()

                if existing_withdrawal is None:
                    new_withdrawal = WithdrawalHistory(
                        withdrawal_id=withdrawal['uuid'],
                        user_id=user_id,
                        timestamp=int(withdrawal['requested_at']),
                        symbol=symbol,
                        amount=withdrawal['amount']
                    )
                    new_withdrawals.append(new_withdrawal)

        db.session().add_all(new_withdrawals)
        db.session().commit()