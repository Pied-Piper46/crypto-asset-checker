import os
import json
import requests
import hmac
import hashlib
import time
import urllib.parse
import ccxt
from pprint import pprint

def get_secrets(secret_file):

    if os.path.exists(secret_file):
        with open(secret_file) as f:
            secrets = json.load(f)
            return secrets

    else:
        print(f"{secret_file}が存在しません。プログラムを終了します。")


secrets = get_secrets("secrets.json")
API_KEY = secrets['API_KEY']
API_SECRET = secrets['API_SECRET']

bitbank = ccxt.bitbank({
    'apiKey': API_KEY,
    'secret': API_SECRET
})


def get_signature(api_secret, nonce, endpoint, body='', params='', method='GET'):

    if method == 'GET':
        if params:
            params_query = urllib.parse.urlencode(params)
            message = nonce + endpoint + '?' + params_query
        else:
            message = nonce + endpoint

    elif method == 'POST':
        body_json = json.dumps(body)
        message = nonce + '$' + body_json
    else:
        raise ValueError('Invalid method')

    signature = hmac.new(bytes(api_secret.encode('ascii')), msg=bytes(message.encode('ascii')), digestmod=hashlib.sha256).hexdigest()

    return signature


def get_jpy_pairs():

    endpoint = "/tickers_jpy"
    response = requests.get('https://public.bitbank.cc' + endpoint).json()

    jpy_pairs = [ticker['pair'] for ticker in response['data']]

    return jpy_pairs


def get_current_price(pair):
    ticker_info = bitbank.fetch_ticker(pair)

    return ticker_info['last']


def get_assets():

    endpoint = "/v1/user/assets"
    nonce = str(int(time.time() * 1000))
    headers = {
        'Content-Type': 'application/json',
        'ACCESS-KEY': API_KEY,
        'ACCESS-NONCE': nonce,
        'ACCESS-SIGNATURE': get_signature(API_SECRET, nonce, endpoint, method='GET')
    }

    response = requests.get('https://api.bitbank.cc' + endpoint, headers=headers).json()
    
    return response


def get_onhand_amount(pair, assets):

    symbol = pair.split('_')[0]

    for item in assets['data']['assets']:
        if item.get("asset") == symbol:
            return float(item.get("onhand_amount"))


def get_jpy_onhand_amount(assets):

    symbol = 'jpy'

    for item in assets['data']['assets']:
        if item.get("asset") == symbol:
            return float(item.get("onhand_amount"))


def get_trade_history(pair):

    trades = []
    since = None

    # Pagination
    while True:
        new_trades = bitbank.fetch_my_trades(symbol=pair, since=since)
        if not new_trades:
            break
        since = new_trades[-1]['timestamp'] + 1
        trades += new_trades
        time.sleep(bitbank.rateLimit / 1000)

    return trades


def calculate_avgcost_and_pnl(pair, trades):

    total_amount = 0.0000
    total_cost = 0.0000
    pnl = 0.0
    avg_cost = 0.0

    for trade in trades:
        if trade['side'] == 'buy':
            total_amount += trade['amount']
            total_amount = round(total_amount, 4)
            total_cost += trade['cost']
            total_cost = round(total_cost, 4)
            avg_cost = total_cost / total_amount

        elif trade['side'] == 'sell':
            if total_amount < trade['amount']:
                pnl += (trade['price'] - avg_cost) * total_amount
                total_amount = 0.0000

            else:
                pnl += (trade['price'] - avg_cost) * trade['amount']
                total_amount -= trade['amount']
                total_amount = round(total_amount, 4)
                total_cost = total_amount * avg_cost
                total_cost = round(total_cost, 4)
            
    return avg_cost, pnl


def evaluate_pnl(pair, assets, trades):

    current_price = get_current_price(pair)
    onhand_amount = get_onhand_amount(pair, assets)
    avg_price, realized_pnl = calculate_avgcost_and_pnl(pair, trades)

    if onhand_amount:
        unrealized_pnl = (current_price - avg_price) * onhand_amount
        evaluation_cost = current_price * onhand_amount
        unrealized_pnl_rate = (unrealized_pnl / evaluation_cost) * 100
    else:
        avg_price = 0
        evaluation_cost = 0
        unrealized_pnl = 0
        unrealized_pnl_rate = 0

    return {
        "symbol": pair.split('_')[0],
        "onhand_amount": onhand_amount,
        "current_price": current_price,
        "evaluation_cost": evaluation_cost,
        "avg_price": avg_price,
        "unrealized_pnl": unrealized_pnl,
        "unrealized_pnl_rate": unrealized_pnl_rate,
        "realized_pnl": realized_pnl
    }


def all_pairs_results():
    
    results = {}
    # jpy_pairs = get_jpy_pairs()
    jpy_pairs = ['btc_jpy', 'eth_jpy', 'xrp_jpy', 'bcc_jpy'] # For simplicity, only those transactions that have occurred in the past are extracted.
    assets = get_assets()

    # add jpy data
    jpy_onhand_amount = get_jpy_onhand_amount(assets)
    results['jpy'] = {
        "symbol": 'jpy',
        "onhand_amount": jpy_onhand_amount,
        "current_price": 0,
        "evaluation_cost": jpy_onhand_amount,
        "avg_price": 0,
        "unrealized_pnl": 0,
        "unrealized_pnl_rate": 0,
        "realized_pnl": 0
    }

    # results of crypto trades
    for pair in jpy_pairs:
        trades = get_trade_history(pair)

        if trades:
            result_json = evaluate_pnl(pair, assets, trades)
            results[pair] = result_json

    return results


def calculate_summary(results):

    total_evaluation_cost = sum([value['evaluation_cost'] for value in results.values()])
    total_unrealized_pnl = sum([value['unrealized_pnl'] for value in results.values()])
    total_realized_pnl = sum([value['realized_pnl'] for value in results.values()])

    return {
        "total_evaluation_cost": total_evaluation_cost,
        "total_unrealized_pnl": total_unrealized_pnl,
        "total_realized_pnl": total_realized_pnl
    }

############################################################################################################


def get_deposits(symbol):

    deposits = []
    since = None

    endpoint = "/v1/user/deposit_history"
    params = {
        "asset": symbol,
    }

    # Pagination
    while True:
        if since is not None:
            params['since'] = since

        nonce = str(int(time.time() * 1000))
        headers = {
            'Content-Type': 'application/json',
            'ACCESS-KEY': API_KEY,
            'ACCESS-NONCE': nonce,
            'ACCESS-SIGNATURE': get_signature(API_SECRET, nonce, endpoint, params=params, method='GET')
        }
        
        response = requests.get('https://api.bitbank.cc' + endpoint, headers=headers, params=params).json()
        new_deposits = response['data']['deposits']
        new_deposits.sort(key=lambda x: x['confirmed_at'], reverse=False)
        if not new_deposits:
            break

        since = int(new_deposits[-1]['confirmed_at']) + 1
        deposits += new_deposits
        time.sleep(bitbank.rateLimit / 1000)

    return deposits


def get_withdrawals(symbol):

    withdrawals = []
    since = None

    endpoint = "/v1/user/withdrawal_history"
    params = {
        "asset": symbol,
    }

    # Pagination
    while True:
        if since is not None:
            params['since'] = since

        nonce = str(int(time.time() * 1000))
        headers = {
            'Content-Type': 'application/json',
            'ACCESS-KEY': API_KEY,
            'ACCESS-NONCE': nonce,
            'ACCESS-SIGNATURE': get_signature(API_SECRET, nonce, endpoint, params=params, method='GET')
        }
        
        response = requests.get('https://api.bitbank.cc' + endpoint, headers=headers, params=params).json()
        new_withdrawals = response['data']['withdrawals']
        new_withdrawals.sort(key=lambda x: x['requested_at'], reverse=False)
        if not new_withdrawals:
            break

        since = int(new_withdrawals[-1]['requested_at']) + 1
        withdrawals += new_withdrawals
        time.sleep(bitbank.rateLimit / 1000)

    return withdrawals