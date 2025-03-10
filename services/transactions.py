import requests
import time

         
def get_all_transactions(address):
    url = "https://toncenter.com/api/v2/getTransactions"
    headers = {"accept": "application/json"}
    params = {
        "address": address,
        "limit": 100,
        "archival": True
    }
    all_transactions = []

    while True:
        response = requests.get(url, headers=headers, params=params)
        time.sleep(1)

        if not response.ok:
            print(f"Error: {response.status_code}, {response.text}")
            break

        data = response.json()
        if not data.get("ok"):
            print(f"API Error: {data.get('error')}")
            break

        transactions = data.get("result", [])
        if not transactions:
            break
                
        all_transactions.extend(transactions)

        # Get lt and hash of the last transaction for pagination
        last_transaction = transactions[-1]
        lt = last_transaction["transaction_id"]["lt"]
        hash_ = last_transaction["transaction_id"]["hash"]

        # Update params for the next request
        params["lt"] = lt
        params["hash"] = hash_

    return all_transactions

# Usage
address = "UQBSvj46DEn3nVhiS1bZePE1uapo_S6e-ocW-tX1ic6t97AZ" # our wallet
transactions = get_all_transactions(address)
print(f"Total transactions fetched: {len(transactions)}")