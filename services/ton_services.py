import time
from decimal import Decimal

import requests
from pytonlib.utils.address import detect_address


def _fetch_address(master_address):
    addr = detect_address(master_address)
    addr = addr['bounceable']['b64url']
    return addr


def _get_jetton_price(master_address):
    fr_addr = _fetch_address(master_address)
    url = f'https://jetton-index.tonscan.org/dyor/api/proxy/jettons/addr/{fr_addr}/details'
    time.sleep(1)
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    price = response['cachedJetton']['priceUsd']
    price = Decimal(price)
    return price


def _get_ton_price_binance():
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {
        "symbol": "TONUSDT"  # Trading pair symbol (TON/USDT)
    }
    try:
        time.sleep(1)
        response = requests.get(url, params=params)
        data = response.json()
        ton_price = data["price"]
        ton_price = Decimal(ton_price)
        return ton_price
    except Exception as e:
        print(f"Error fetching TON price: {e}")


def _get_jettons(wallet_address):
    url = f'https://preview.toncenter.com/api/v3/jetton/wallets?owner_address={wallet_address}&exclude_zero_balance=true&limit=50&offset=0'
    wallet = {}
    time.sleep(1)
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    jettons = response['jetton_wallets']
    metadata = response['metadata']
    for jetton in jettons:
        jetton_code = jetton['jetton']
        balance = jetton['balance']
        balance = int(balance)
        jetton_metadata = metadata.get(jetton_code, {})
        jetton_info = jetton_metadata.get('token_info', {})[0]
        decimal = int(jetton_info.get('extra', {}).get('decimals', 9))
        jetton_symbol = jetton_info.get('symbol', '')
        jetton_name = jetton_info.get('name', '')
        address = jetton.get('jetton', '')
        try:
            price = _get_jetton_price(address)
        except Exception as e:
            price = 0
        value = {
            'balance': balance,
            'decimal': decimal,
            'symbol': jetton_symbol,
            'name': jetton_name,
            'price': price
        }
        wallet[address] = value
    return wallet


def _get_ton_balance(wallet_address):
    url = f'https://preview.toncenter.com/api/v3/accountStates?address={wallet_address}&include_boc=false'
    wallet = {}
    time.sleep(1)
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    accounts = response['accounts']
    if len(accounts) > 0:
        account = accounts[0]
        balance = account['balance']
        balance = int(balance)
        decimal = 9
        price = _get_ton_price_binance()
        value = {
            'balance': balance,
            'decimal': decimal,
            'symbol': 'TON',
            'name': 'TONCOIN',
            'price': price
        }
        wallet['TON'] = value
    return wallet


def get_balance(wallet_address):
    jettons = _get_jettons(wallet_address)
    ton = _get_ton_balance(wallet_address)
    if ton is None or jettons is None:
        return None
    else:
        wallet = {**ton, **jettons}
        return wallet
