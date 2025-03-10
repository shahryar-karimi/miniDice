import time

import requests
from pytonlib.utils.address import detect_address


def _get_coin_price(ton_or_address):
    url = "https://tonapi.io/v2/rates"
    params = {
        'tokens': ton_or_address,
        'currencies': 'usd'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    response = response.json()
    return response['rates'][ton_or_address]['prices']['USD']


def _get_ton_balance(wallet_address):
    url = f'https://preview.toncenter.com/api/v3/accountStates?address={wallet_address}&include_boc=false'
    wallet = {}
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    accounts = response['accounts']
    if len(accounts) > 0:
        account = accounts[0]
        balance = account['balance']
        balance = int(balance)
        decimal = 9
        price = _get_coin_price('TON')
        value = {
            'balance': balance,
            'decimal': decimal,
            'value': (price * (balance / 10 ** decimal))
        }
        wallet['TON'] = value
    return wallet


def _get_jettons(wallet_address):
    url = f'https://preview.toncenter.com/api/v3/jetton/wallets?owner_address={wallet_address}&exclude_zero_balance=true&limit=50&offset=0'
    wallet = {}
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    jettons = response['jetton_wallets']
    metadata = response['metadata']
    for jetton in jettons:
        jetton_code = jetton['jetton']
        address = detect_address(f"{jetton_code}")

        friendly_address = address['bounceable']['b64url']
        price = _get_coin_price(friendly_address)
        price = float(price)

        balance = jetton['balance']
        balance = int(balance)
        jetton_metadata = metadata.get(jetton_code, {})
        jetton_info = jetton_metadata.get('token_info', {})[0]
        decimal = int(jetton_info.get('extra', {}).get('decimals', 0))
        jetton_symbol = jetton_info.get('symbol', '')
        value = {
            'balance': balance,
            'decimal': decimal,
            'value': (price * (balance / 10 ** decimal))
        }
        wallet[jetton_symbol] = value
    return wallet


def get_balance(wallet_address):
    jettons = _get_jettons(wallet_address)
    time.sleep(2)
    ton = _get_ton_balance(wallet_address)
    time.sleep(2)
    if ton is None or jettons is None:
        return None
    else:
        wallet = {**ton, **jettons}
        return wallet
