from . import db
from utilities import get_all_deposit_history

class DepositHistory(db.Model):

    __tablename__ = 'deposit_history'

    deposit_id = db.Column(db.String(120), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    symbol = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def get_deposit_history(user_id):
        return DepositHistory.query.filter_by(user_id=user_id).all()

    def add_new_deposits():

        user_id = 1 # fixed so far
        new_deposits = []
        all_deposit_history = get_all_deposit_history()
        for symbol, deposits in all_deposit_history.items():
            for deposit in deposits:
                existing_deposit = DepositHistory.query.filter_by(deposit_id=deposit['uuid']).first()

                if existing_deposit is None:
                    new_deposit = DepositHistory(
                        deposit_id=deposit['uuid'],
                        user_id=user_id,
                        timestamp=int(deposit['confirmed_at']),
                        symbol=symbol,
                        amount=deposit['amount']
                    )
                    new_deposits.append(new_deposit)

        db.session().add_all(new_deposits)
        db.session().commit()