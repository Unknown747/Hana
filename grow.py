import requests
import time
import json

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
                    gardenMilestoneRewardInfo {
                        id
                        gardenDepositCountWhenLastCalculated
                        lastAcquiredAt
                        createdAt
                    }
                    gardenMembers {
                        id
                        sub
                        name
                        iconPath
                        depositCount
                    }
                }
            }
        """,
        "operationName": "GetGardenForCurrentUser"
    }
    data_GetSnsShare = {
        "query": """
            query GetSnsShare($actionType: SnsShareActionType!, $snsType: SnsShareSnsType!) {
                getSnsShare(actionType: $actionType, snsType: $snsType) {
                    lastShareBonusAt
                    isExistNewBonus
                }
            }
        """,
        "variables": {"actionType": "GARDEN_REWARD", "snsType": "X"},
        "operationName": "GetSnsShare"
    }
    data_GetSnsShare2 = {
        "query": """
            query GetSnsShare($actionType: SnsShareActionType!, $snsType: SnsShareSnsType!) {
                getSnsShare(actionType: $actionType, snsType: $snsType) {
                    lastShareBonusAt
                    isExistNewBonus
                }
            }
        """,
        "variables": {"actionType": "GROW", "snsType": "X"},
        "operationName": "GetSnsShare"
    }

    for _ in range(wokwok):
        response_issue = requests.post(url, headers=headers, data=json.dumps(data_issue))
        issue_data = response_issue.json()
        
        if "errors" in issue_data:
            error_message = issue_data["errors"][0].get("message", "")
            if error_message == "Unauthorized":
                print("Unauthorized access detected. Stopping script.")
                return 

        print("Points =>", issue_data)
        
        response_commit = requests.post(url, headers=headers, data=json.dumps(data_commit))
        response_1 = requests.post(url, headers=headers, data=json.dumps(data_CurrentUser))
        response_1data = response_1.json()
        
        if "errors" in response_1data:
            error_message = response_1data["errors"][0].get("message", "")
            if error_message == "Unauthorized":
                print("Unauthorized access detected. Stopping script.")
                return 

        if "data" in response_1data and "currentUser" in response_1data["data"]:
            namauser = response_1data["data"]["currentUser"]["name"]
            totalpoint = response_1data["data"]["currentUser"]["totalPoint"]
            print("User :", namauser, "| Total Points :", totalpoint)
        else:
            print("Data no available", response_1data)
        
        response_2 = requests.post(url, headers=headers, data=json.dumps(data_GetGardenForCurrentUser))
        response_3 = requests.post(url, headers=headers, data=json.dumps(data_GetSnsShare))
        response_4 = requests.post(url, headers=headers, data=json.dumps(data_GetSnsShare2))

        time.sleep(1)

wokwok = int(input("Jumlah grows: "))
run_requests(wokwok)
