import os
import json
import requests
import hmac
import hashlib
import time
import urllib.parse
import ccxt
from pprint import pprint

from config import API_KEY, API_SECRET
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


def get_tickers_jpy():

    endpoint = "https://public.bitbank.cc/tickers_jpy"
    response = requests.get(endpoint).json()

    return response['data']


def get_current_price_noapi(pair, tickers):

    target_ticker = next(filter(lambda d: d['pair'] == pair, tickers), None)
    return float(target_ticker['last'])


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


def get_onhand_amount(symbol, assets):

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


def get_all_trade_history():

    results = {}
    # jpy_pairs = get_jpy_pairs()
    jpy_pairs = ['btc_jpy', 'eth_jpy', 'xrp_jpy', 'bcc_jpy', 'ltc_jpy']

    for pair in jpy_pairs:
        trades = get_trade_history(pair)
        results[pair] = trades

    return results


def get_deposit_history(symbol):

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


def get_all_deposit_history():

    results = {}
    # jpy_pairs = get_jpy_pairs()
    jpy_pairs = ['btc_jpy', 'eth_jpy', 'xrp_jpy', 'bcc_jpy', 'ltc_jpy']

    jpy_deposit_history = get_deposit_history('jpy')
    results['jpy'] = jpy_deposit_history

    for pair in jpy_pairs:
        symbol = pair.split('_')[0]
        deposit_history = get_deposit_history(symbol)
        results[symbol] = deposit_history

    return results


def get_withdrawal_history(symbol):

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


def get_all_withdrawal_history():
    
    results = {}
    # jpy_pairs = get_jpy_pairs()
    jpy_pairs = ['btc_jpy', 'eth_jpy', 'xrp_jpy', 'bcc_jpy', 'ltc_jpy']

    jpy_withdrawal_history = get_withdrawal_history('jpy')
    results['jpy'] = jpy_withdrawal_history

    for pair in jpy_pairs:
        symbol = pair.split('_')[0]
        withdrawal_history = get_withdrawal_history(symbol)
        results[symbol] = withdrawal_history

    return results


def calculate_net_investment(symbol, deposit_history, withdrawal_history):

    deposits_by_symbol = [deposit for deposit in deposit_history if deposit.symbol == symbol]
    withdrawals_by_symbol = [withdrawal for withdrawal in withdrawal_history if withdrawal.symbol == symbol]
    total_deposits = sum([deposit.amount for deposit in deposits_by_symbol])
    total_withdrawals = sum([withdrawal.amount for withdrawal in withdrawals_by_symbol])

    return total_deposits - total_withdrawals


def calculate_avgcost_and_pnl(trades):

    purchased_amount = 0
    total_cost = 0
    pnl = 0
    avg_cost = 0

    for trade in trades:
        if trade.side == 'buy':
            purchased_amount += trade.amount
            total_cost += trade.amount * trade.price
            avg_cost = total_cost / purchased_amount

        elif trade.side == 'sell':
            if trade.amount > purchased_amount:
                pnl += (trade.price - avg_cost) * purchased_amount
                purchased_amount = 0
                total_cost = 0

            else:
                pnl += (trade.price - avg_cost) * trade.amount
                purchased_amount -= trade.amount
                total_cost = purchased_amount * avg_cost
            
    return avg_cost, pnl


def evaluate_trade(pair, assets, tickers, trades):

    symbol = pair.split('_')[0]
    current_price = get_current_price_noapi(pair, tickers)
    onhand_amount = get_onhand_amount(symbol, assets)
    trades_by_pair = [trade for trade in trades if trade.pair == pair]

    if trades_by_pair:
        avg_price, realized_pnl = calculate_avgcost_and_pnl(trades_by_pair)

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
            "symbol": symbol,
            "onhand_amount": onhand_amount,
            "current_price": current_price,
            "evaluation_cost": evaluation_cost,
            "avg_price": avg_price,
            "unrealized_pnl": unrealized_pnl,
            "unrealized_pnl_rate": unrealized_pnl_rate,
            "realized_pnl": realized_pnl
        }
    else:
        pass


def trade_results(trades, deposit_history, withdrawal_history):
    
    results = {}
    # jpy_pairs = get_jpy_pairs()
    jpy_pairs = ['btc_jpy', 'eth_jpy', 'xrp_jpy', 'bcc_jpy', 'ltc_jpy'] # For simplicity, only those transactions that have occurred in the past are extracted.
    assets = get_assets()
    tickers = get_tickers_jpy()

    # get jpy data
    jpy_onhand_amount = get_onhand_amount('jpy', assets)
    jpy_net_investment = calculate_net_investment('jpy', deposit_history, withdrawal_history)
    results['jpy'] = {
        "symbol": 'jpy',
        "onhand_amount": jpy_onhand_amount,
        "net_investment": jpy_net_investment,
        "current_price": 0,
        "evaluation_cost": jpy_onhand_amount,
        "avg_price": 0,
        "unrealized_pnl": 0,
        "unrealized_pnl_rate": 0,
        "realized_pnl": 0
    }

    # get results of crypto trades
    for pair in jpy_pairs:
        result_json = evaluate_trade(pair, assets, tickers, trades)
        if result_json:
            results[pair] = result_json

            symbol = pair.split('_')[0]
            net_investment = calculate_net_investment(symbol, deposit_history, withdrawal_history)
            results[pair]['net_investment'] = net_investment

    return results


def calculate_summary(results):

    total_evaluation_cost = sum([value['evaluation_cost'] for value in results.values()])
    total_unrealized_pnl = sum([value['unrealized_pnl'] for value in results.values()])
    total_realized_pnl = sum([value['realized_pnl'] for value in results.values()])

    # calculate total_unrealized_pnl_rate
    total_investment = total_evaluation_cost - results['jpy']['evaluation_cost']
    total_unrealized_pnl_rate = total_unrealized_pnl / total_investment * 100

    return {
        "total_evaluation_cost": total_evaluation_cost,
        "total_unrealized_pnl": total_unrealized_pnl,
        "total_unrealized_pnl_rate": total_unrealized_pnl_rate,
        "total_realized_pnl": total_realized_pnl
    }