import time
import requests
from pytonlib.utils.address import detect_address


def _fetch_address(master_address):
    addr = detect_address(master_address)
    addr = addr['bounceable']['b64url']
    return addr


def _get_jetton_price(master_address):
    fr_addr = _fetch_address(master_address)
    url = f'https://jetton-index.tonscan.org/dyor/api/proxy/jettons/addr/{fr_addr}/details'
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    price = response['cachedJetton']['priceUsd']
    price = float(price)
    return price

def _get_ton_price_binance():
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {
        "symbol": "TONUSDT"  # Trading pair symbol (TON/USDT)
    }    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        ton_price = data["price"]
        return float(ton_price)    
    except Exception as e:
        print(f"Error fetching TON price: {e}")    


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
        jetton_name = jetton_info.get('name', '')
        address = jetton.get('jetton', '')
        try:
            price = _get_jetton_price(address)
        except Exception as e:
            price = 0
        usd_value = (balance / 10 ** decimal) * price
        value = {
            'balance': balance,
            'decimal': decimal,
            'symbol': jetton_symbol,
            'name': jetton_name,
            'price': price,
            'usd_value': usd_value
        }
        wallet[address] = value
    return wallet
    

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
        price = _get_ton_price_binance()
        usd_value = (balance / 10**decimal) * price
        value = {
            'balance': balance,
            'decimal': decimal,
            'symbol': 'TON',
            'name': 'TONCOIN',
            'price': price,
            'usd_value': usd_value
        }
        wallet['TON'] = value
    return wallet


def get_balance(wallet_address):
    jettons = _get_jettons(wallet_address)
    time.sleep(0.5)
    ton = _get_ton_balance(wallet_address)
    time.sleep(0.5)
    if ton is None or jettons is None:
        return None
    else:
        wallet = {**ton, **jettons}
        return wallet
    

if __name__ == "__main__":
    wallet_address = "UQBwHP7QWC45YmO-6Rzj_pXGy7KavYgAkiPO5Qy2ZrKdSJ_D"
    print(get_balance(wallet_address))
    # master_address = '0:84AB3DB1DFE51BFC43B8639EFDF0D368A8AC35B4FFED27A6FDCBE5F40B8BAFB3'
    
    
