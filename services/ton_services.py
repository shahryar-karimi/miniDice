import time
import requests


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
        value = {
            'balance': balance,
            'decimal': decimal,
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
        balance = jetton['balance']
        balance = int(balance)
        jetton_metadata = metadata.get(jetton_code, {})
        jetton_info = jetton_metadata.get('token_info', {})[0]
        decimal = int(jetton_info.get('extra', {}).get('decimals', 0))
        jetton_symbol = jetton_info.get('symbol', '')
        value = {
            'balance': balance,
            'decimal': decimal,
        }
        wallet[jetton_symbol] = value
    return wallet
    
    
def _get_ids(list_of_coins):
    url = "https://api.coingecko.com/api/v3/coins/list"

    payload = {}
    headers = {
    'accept': 'application/json',
    'x-cg-demo-api-key': 'CG-acXGFe42mUsK8w9W6oPnhGVE'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response.raise_for_status()
    response = response.json()
    output = [coin_data for coin_data in response if coin_data['name'] in list_of_coins]

    return output

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
    
    
    