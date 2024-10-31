import requests
import time
import json
import os

def load_bearer_token():
    if os.path.exists('bearer.txt'):
        with open('bearer.txt', 'r') as file:
            return file.read().strip()
    else:
        return refresh_bearer_token()

def load_refresh_token():
    if os.path.exists('token.txt'):
        with open('token.txt', 'r') as file:
            return file.read().strip()
    else:
        print("File token.txt tidak ditemukan.")
        return None

def refresh_bearer_token():
    refresh_token = load_refresh_token()
    if not refresh_token:
        print("Gagal memuat refresh_token.")
        return None

    url = "htt"+"ps:"+"//secur"+"etoken.go"+"oglea"+"pis.com/v1/tok"+"en?key"+"=AIzaSyDip"+"zN0"+"VRfTPn"+"MG"+"hQ"+"5PSz"+"O27C"+"xm3D"+"ohJGY"
    body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    headers = {
        'accept': '*/*',
        'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'x-client-version': 'Chrome/JsCore/10.12.0/FirebaseCore-web',
        'origin': 'https://hanafuda.hana.network/',
        'Referer': 'https://hanafuda.hana.network/',  
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    response = requests.post(url, headers=headers, data=body)
    response_data = response.json()
    if "access_token" in response_data:
        new_token = response_data["access_token"]
        with open('bearer.txt', 'w') as file:
            file.write(new_token)
        print("Sesi diperbarui di bearer.txt")
        return new_token
    else:
        print("Gagal memperbarui Sesi:", response_data)
        return None

def run_requests():
    url = "https://hanafuda-backend-app-520478841386.us-central1.run.app/graphql"

    data_issue = {
        "query": "mutation issueGrowAction { issueGrowAction }",
        "operationName": "issueGrowAction"
    }
    data_commit = {
        "query": "mutation commitGrowAction { commitGrowAction }",
        "operationName": "commitGrowAction"
    }
    data_CurrentUser = {
        "query": """
            query CurrentUser {
                currentUser {
                    id
                    sub
                    name
                    iconPath
                    depositCount
                    totalPoint
                    evmAddress {
                        userId
                        address
                    }
                    inviter {
                        id
                        name
                    }
                }
            }
        """,
        "operationName": "CurrentUser"
    }
    data_GetGardenForCurrentUser = {
        "query": """
            query GetGardenForCurrentUser {
                getGardenForCurrentUser {
                    id
                    inviteCode
                    gardenDepositCount
                    gardenStatus {
                        id
                        activeEpoch
                        growActionCount
                        gardenRewardActionCount
                    }
                }
            }
        """,
        "operationName": "GetGardenForCurrentUser"
    }

    headers = {
        'accept': 'application/graphql-response+json, application/json',
        'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
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

    while True:
        token = refresh_bearer_token()
        if not token:
            print("Gagal memperbarui Sesi.")
            return
        headers['authorization'] = f'Bearer {token}'

        response_garden = requests.post(url, headers=headers, data=json.dumps(data_GetGardenForCurrentUser))
        if response_garden.status_code == 200:
            garden_data = response_garden.json()
            growActionCount = garden_data.get("data", {}).get("getGardenForCurrentUser", {}).get("gardenStatus", {}).get("growActionCount", 0)
            print(f"Jumlah grows : {growActionCount}")

            if growActionCount == 0:
                print("jumlah grow 0, turu 30 menit...")
                time.sleep(1800)
                continue

        else:
            print("Gagal mengambil Jumlah Grow:", response_garden.status_code)
            return
        for _ in range(growActionCount):
            response_issue = requests.post(url, headers=headers, data=json.dumps(data_issue))
            if response_issue.status_code == 200:
                issue_data = response_issue.json()
                print("Points =>", issue_data)

            response_commit = requests.post(url, headers=headers, data=json.dumps(data_commit))
            
            response_current_user = requests.post(url, headers=headers, data=json.dumps(data_CurrentUser))
            if response_current_user.status_code == 200:
                response_1data = response_current_user.json()
                if "data" in response_1data and "currentUser" in response_1data["data"]:
                    namauser = response_1data["data"]["currentUser"]["name"]
                    totalpoint = response_1data["data"]["currentUser"]["totalPoint"]
                    print("User :", namauser, "| Total Points :", totalpoint)
                else:
                    print("Data no available", response_1data)

            time.sleep(0)
run_requests()
