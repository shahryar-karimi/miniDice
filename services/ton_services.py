import time
import requests
from pytonlib.utils.address import detect_address
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def _get_jetton_price(jetton_address):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in background
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = f"https://tonscan.org/jetton/{jetton_address}"
    driver.get(url)
    time.sleep(2)
    price_element = driver.find_element(By.CLASS_NAME, "jetton-meta-price__value")  # Adjust class name
    price = price_element.text
    price = price.replace('$', '')
    price = float(price)
    driver.quit()
    return price

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
            'value': (price * (balance / 10**decimal))
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

        # Get the friendly (user-readable) address
        friendly_address = address['bounceable']['b64url']
        # price = _get_jetton_price(friendly_address)
        price = _get_coin_price(friendly_address)
        price = float(price)
        if price == 0:
            for i in range(6):
                try:
                    price = _get_jetton_price(friendly_address)
                    if price:
                        break
                except:
                    time.sleep(3 + i)
                    
        balance = jetton['balance']
        balance = int(balance)
        jetton_metadata = metadata.get(jetton_code, {})
        jetton_info = jetton_metadata.get('token_info', {})[0]
        decimal = int(jetton_info.get('extra', {}).get('decimals', 0))
        jetton_symbol = jetton_info.get('symbol', '')
        address = jetton.get('address', '')
        value = {
            'balance': balance,
            'decimal': decimal,
            'value': (price * (balance / 10**decimal))
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
    
    
    