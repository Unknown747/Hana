import os, requests, json, time, threading
from web3 import Web3
from dotenv import load_dotenv

class HanaTransaction:
    def __init__(self, private_key, token, api_key, provider, contract_address):
        self.private_key = private_key
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.token = token
        self.api_key = api_key
        self.bearer_token = ""
        self.web3 = Web3(Web3.HTTPProvider(provider))
        self.wallet = self.web3.eth.account.from_key(private_key).address
        self.contract_abi = [
            {
                "inputs": [],
                "name": "depositETH",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
        self.lock = threading.Lock()
        self.token_refreshed = False

    def refresh_token(self):
        url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"
        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://hanafuda.hana.network/",
            "Referer": "https://hanafuda.hana.network/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.token
        }
        try:
            response = requests.post(url, headers=headers, data=data)
            response_data = response.json()
            if 'access_token' in response_data:
                self.bearer_token = response_data['access_token']
                with open("bearer.txt", "w") as file:
                    file.write(self.bearer_token)
                print("Bearer token successfully updated.")
                return True
            else:
                print("Failed to update bearer token.")
                return False
        except Exception as error:
            print(f"Error refreshing token: {error}")
            return False

    def initialize_token(self):
        if os.path.exists("bearer.txt"):
            with open("bearer.txt", "r") as file:
                self.bearer_token = file.read().strip()
            print("Bearer token loaded from file.")
        else:
            print("No bearer token found. Refreshing token...")
            if not self.refresh_token():
                print("Failed to refresh bearer token. Exiting.")
                exit(1)

    def transaction_receipt(self, tx_hash):
        while True:
            try:
                receipt = self.web3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    return True
            except Exception as e:
                pass

    def submit_transaction(self, tx_hash):
        url = "https://hanafuda-backend-app-520478841386.us-central1.run.app/graphql"
        headers = {
            "accept": "application/graphql-response+json, application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.bearer_token}",
            "priority": "u=1, i"
        }

        data = {
            "query": "mutation SyncEthereumTx($chainId: Int!, $txHash: String!) {\n  syncEthereumTx(chainId: $chainId, txHash: $txHash)\n}",
            "variables": { "chainId": 42161, "txHash": f"0x{tx_hash}" },
            "operationName": "SyncEthereumTx"
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_json = response.json()

            if 'errors' in response_json and any(error['extensions']['code'] == 'UNAUTHORIZED' for error in response_json['errors']):
                print("Unauthorized error detected. Refreshing token...")
                with self.lock:
                    if not self.token_refreshed:
                        self.refresh_token()
                self.submit_transaction(tx_hash)

            elif response.status_code == 200:
                print(f"Transaction sent with hash: 0x{tx_hash}")
            else:
                print(f"Failed to submit request. Status code: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error submitting transaction: {e}")

    def submit_transactions_in_parallel(self, tx_hashes):
        threads = []
        
        for tx_hash in tx_hashes:
            thread = threading.Thread(target=self.submit_transaction, args=(tx_hash,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()

    def execute_batch_transactions(self, batch_size=3):
        self.initialize_token()
        
        while True:
            tx_hashes = []
            print("Starting new batch of transaction execution...")

            while len(tx_hashes) < batch_size:
                try:
                    amount_in_wei = Web3.to_wei(0.00000042, 'ether')
                    contract = self.web3.eth.contract(address=self.contract_address, abi=self.contract_abi)
                    
                    transaction = contract.functions.depositETH().build_transaction({
                        'from': self.wallet,
                        'nonce': self.web3.eth.get_transaction_count(self.wallet, "latest"),
                        'value': amount_in_wei,
                        'gas': 200000
                    })

                    signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=self.private_key)
                    tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction).hex()
                    tx_hashes.append(tx_hash)

                    if self.transaction_receipt(tx_hash):
                        print(f"Transaction receipt confirmed: 0x{tx_hash}")
                    else:
                        print(f"Transaction 0x{tx_hash} not confirmed yet, retrying...")

                except Exception as e:
                    print(f"Error executing transaction: {e}")
                    break

            if len(tx_hashes) == batch_size:
                print("Submitting batch of transactions...")
                self.submit_transactions_in_parallel(tx_hashes)
                print("Batch transactions submitted.")
            
            print("Waiting before starting the next batch of transactions...")
            time.sleep(5)

load_dotenv()

private_key = os.getenv("PRIVATE_KEY")
token = os.getenv("TOKEN")
api_key = os.getenv("API_KEY")

if not private_key:
    print("Error: Private key not found.")
elif not token:
    print("Error: Token not found.")
elif not api_key:
    print("Error: API key not found.")
else:
    print("======================================")
    print("Enter 1 to use the Arbitrum network")
    print("Enter 2 to use the Base network")
    print("======================================")
    type_network = int(input(""))
    if type_network == 1:
        transaction = HanaTransaction(private_key, token, api_key, "https://arb1.arbitrum.io/rpc", "0xC5bf05cD32a14BFfb705Fb37a9d218895187376c")
        transaction.execute_batch_transactions()
    elif type_network == 2:
        transaction = HanaTransaction(private_key, token, api_key, "https://mainnet.base.org", "0xc5bf05cd32a14bffb705fb37a9d218895187376c")
        transaction.execute_batch_transactions()
    else:
        print("Invalid choice. Please choose either 1 or 2.")

