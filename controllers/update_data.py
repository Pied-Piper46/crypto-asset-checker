from flask import Blueprint, redirect, url_for
from models.trade_history import TradeHistory
from models.deposit_history import DepositHistory
from models.withdrawal_history import WithdrawalHistory
import utilities

update_page = Blueprint("update_page", __name__)

@update_page.route("/update-data", methods=['POST'])
def update_data():
    
    TradeHistory.add_new_trades()
    DepositHistory.add_new_deposits()
    WithdrawalHistory.add_new_withdrawals()

    return redirect(url_for('index_page.index'))