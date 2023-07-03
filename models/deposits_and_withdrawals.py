import db
from sqlalchemy import Enum

class DepositsAndWithdrawals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    timestamp = db.Column(db.Datetime, nullable=False)
    symbol = db.Column(db.String(120), nullable=False)
    category = db.Column(Enum('Deposit', 'Withdrawal'), nullable=False)
    amount = db.Column(db.Float, nullable=False)