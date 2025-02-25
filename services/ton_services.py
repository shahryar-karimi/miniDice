import requests


def _get_ton_balance(wallet_address):
    url = f'https://preview.toncenter.com/api/v3/accountStates?address={wallet_address}&include_boc=false'
    wallet = {}
    try:
        response = requests.get(url)
        response.raise_for_status()
        response = response.json()  
        account = response['accounts'][0]
        balance = account['balance']
        balance = float(balance) / 10**9
        wallet['TON'] = balance
        return wallet
                
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def _get_jettons(wallet_address):
    
    url = f'https://preview.toncenter.com/api/v3/jetton/wallets?owner_address={wallet_address}&exclude_zero_balance=true&limit=50&offset=0'
    wallet = {}
    try:
        response = requests.get(url)
        response.raise_for_status()
        response = response.json()  
        jettons = response['jetton_wallets']
        metadata = response['metadata']
        for jetton in jettons:
            jetton_code = jetton['jetton']
            balance = jetton['balance']
            balance = float(balance) / 10**9
            jetton_metadata = metadata.get(jetton_code, {})
            jetton_info = jetton_metadata.get('token_info', {})[0]
            jetton_symbol = jetton_info.get('symbol', '')
            wallet[jetton_symbol] = balance
        return wallet
            
        
        
                
    except requests.exceptions.RequestException as e:
        print(e)
        return None
    

def get_balance(wallet_address):
    ton = _get_ton_balance(wallet_address)
    jettons = _get_jettons(wallet_address)
    if ton is None or jettons is None:
        return None
    else:
        wallet = {**ton, **jettons}
        return wallet
    


wallet = 'UQBwHP7QWC45YmO-6Rzj_pXGy7KavYgAkiPO5Qy2ZrKdSJ_D'
print(get_balance(wallet))