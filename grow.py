import requests
import time

def load_bearer_token():
    with open('bearer.txt', 'r') as file:
        return file.read().strip()

def run_requests(wokwok):
    url = "https://hanafuda-backend-app-520478841386.us-central1.run.app/graphql"
    headers = {
        'accept': 'application/graphql-response+json, application/json',
        'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': f'Bearer {load_bearer_token()}',
        'content-type': 'application/json',
        'origin': 'https://hanafuda.hana.network',
        'referer': 'https://hanafuda.hana.network/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    data_issue = '{"query":"mutation issueGrowAction {\\n  issueGrowAction\\n}","operationName":"issueGrowAction"}'
    data_commit = '{"query":"mutation commitGrowAction {\\n  commitGrowAction\\n}","operationName":"commitGrowAction"}'

    for _ in range(wokwok):
        response_issue = requests.post(url, headers=headers, data=data_issue)
        print("Points => ", response_issue.json())
        response_commit = requests.post(url, headers=headers, data=data_commit)
        time.sleep(1)

wokwok = int(input("jumlah grows : "))
run_requests(wokwok)
