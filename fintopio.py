
import random
import time
import sys
import re
import json
import requests
from urllib.parse import unquote, parse_qs
from datetime import datetime


api = "https://fintopio-tg.fintopio.com/api"

header = {
      "Accept": "application/json, text/plain, */*",
      "Accept-Encoding": "gzip, deflate, br",
      "Accept-Language": "en-US,en;q=0.9",
      "Referer": "https://fintopio-tg.fintopio.com/",
      "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128", "Microsoft Edge WebView2";v="128"',
      "Sec-Ch-Ua-Mobile": "?0",
      "Sec-Ch-Ua-Platform": "Windows",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
    }

def load_credentials():
    # Membaca token dari file dan mengembalikan daftar token
    try:
        with open('fintopio_query.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        # print("Token berhasil dimuat.")
        return queries
    except FileNotFoundError:
        print("File query_id.txt tidak ditemukan.")
        return 
    except Exception as e:
        print("Terjadi kesalahan saat memuat query:", str(e))
        return 

def banner():
    print("""
        ========== FINTOPIO BOT ==========
        Join Group : t.me/sansxgroup
        Github     : github.com/boytegar 
    """)

def print_(word):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"[{now}] {word}")

def response_data(response):
        if response.status_code >= 500:
            print_(f"Error {response.status_code}")
            return None
        elif response.status_code >= 400:
            print_(f"Error {response.status_code}")
            return None
        elif response.status_code >= 200:
            return response.json()
        else:
            return None

def parse_query(query: str):
    parsed_query = parse_qs(query)
    parsed_query = {k: v[0] for k, v in parsed_query.items()}
    user_data = json.loads(unquote(parsed_query['user']))
    parsed_query['user'] = user_data
    return parsed_query

def get(id):
        tokens = json.loads(open("tokens.json").read())
        if str(id) not in tokens.keys():
            return None
        return tokens[str(id)]

def save(id, token):
        tokens = json.loads(open("tokens.json").read())
        tokens[str(id)] = token
        open("tokens.json", "w").write(json.dumps(tokens, indent=4))

def make_request(self, method, url, headers, json=None, data=None):
    retry_count = 0
    while True:
        time.sleep(2)
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, json=json)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json, data=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=json, data=data)
        else:
            raise ValueError("Invalid method.")
        
        if response.status_code >= 500:
            if retry_count >= 4:
                self.print_(f"Status Code: {response.status_code} | {response.text}")
                return None
            retry_count += 1
            return None
        elif response.status_code >= 400:
            self.print_(f"Status Code: {response.status_code} | {response.text}")
            return None
        elif response.status_code >= 200:
            return response

def getdata(token):
    header['Authorization'] = f"Bearer {token}"
    response = requests.get(api+"/referrals/data", headers=header)
    data = response_data(response)
    return data

def checkin(token):
    try:
        url = api + "/daily-checkins"
        header['Authorization'] = f"Bearer {token}"
        header['Webapp'] = "true"
        response = requests.post(url, headers=header)
        data = response_data(response)
        return data
        
    except:
        print_('[checkin] failed, restarting')

def diamond(token):
    urldiamondstate = '/clicker/diamond/state'
    header['Authorization'] = f"Bearer {token}"
    header['Webapp'] = "true"
    try:
        response = requests.get(api+urldiamondstate, headers=header)
        data = response_data(response)
        return data
        

    except:
        print_('[asteroid] error restarting')
        time.sleep(5)
        main()

def start_task(token, id):
    header['Authorization'] = f"Bearer {token}"
    header['Webapp'] = "true"
    urlstart = f'/hold/tasks/{id}/start'
    response = requests.post(api+urlstart, headers=header)
    return response_data(response)

def claim_task(token, id):
    header['Authorization'] = f"Bearer {token}"
    header['Webapp'] = "true"
    urlclaim = f'/hold/tasks/{id}/claim'
    response = requests.post(api+urlclaim, headers=header)
    return response_data(response)

def printdelay(delay):
    now = datetime.now().isoformat(" ").split(".")[0]
    hours, remainder = divmod(delay, 3600)
    minutes, sec = divmod(remainder, 60)
    print(f"[{now}] | Waiting Time: {hours} hours, {minutes} minutes, and {round(sec)} seconds")      

def getlogin(query):
    url = api + "/auth/telegram?"
    header['Webapp'] = 'true'
    response = requests.get(url+query, headers=header)
    data = response_data(response)
    return data

def getname(queries):
    try:
        found = re.search('user=([^&]*)', queries).group(1)
        decoded = unquote(found)
        data = json.loads(decoded)
        return data
    except:
        print_('getname error')



def complete(token, id):
    url = api + "/clicker/diamond/complete"
    header['Authorization'] = f"Bearer {token}"
    payload = {"diamondNumber":id}
    response = requests.post(url, headers=header, json=payload)
    if response.status_code != 200:
        print_('asteroid failed to claim')
        return None
    else:
        return response.status_code


def getfarm(bearer):
    urlfarmstate = '/farming/state'
    try:
        response = requests.get(api+urlfarmstate, headers=header)
        data = response_data(response)
        state =  data['state']
        if state == 'idling':
            startfarm(bearer)
        elif state == 'farming':
            print_('farming not finished yet!')
        elif state == 'farmed':
            claimfarm(bearer)
        else:
            print_('[farming] error ')
    except:
        print_('[farming] error restarting')
        time.sleep(5)   

def startfarm(token):
    try:
        url = api + "/farming/farm"
        header['Authorization'] = f"Bearer {token}"
        header['Webapp'] = "true"
        response = requests.post(url, headers=header)
        if response.status_code == 200:
            print_('farming started!')
    except:
        print_('[farming] failed to start')

def claimfarm(token):
    try:
        url = api + "/farming/claim"
        header['Authorization'] = f"Bearer {token}"
        header['Webapp'] = "true"
        response = requests.post(url, headers=header)
        if response.status_code == 200:
            print_('farming claimed!')
            time.sleep(2)
            startfarm(token)
    except:
        print_('[farming] failed to claim')

def gettask(token):
    try:
        urltasks = api + "/hold/tasks"
        header['Authorization'] = f"Bearer {token}"
        header['Webapp'] = "true"
        response = requests.get(urltasks, headers=header)
        data = response_data(response)
        return data
    except Exception as e:
        print_('[gettask] failed, restarting')

def init(token):
    url = 'https://fintopio-tg.fintopio.com/api/hold/fast/init'
    header['Authorization'] = f"Bearer {token}"
    header['Webapp'] = "true"
    response = requests.get(url, headers=header)
    data = response_data(response)
    return data

def main():
    status_task = 'y' 
    banner()
    while True:
        delay = 1 * random.randint(3600, 3700)
        queries = load_credentials()
        start_time = time.time()
        total_point = 0
        sum = len(queries)
        for index, query in enumerate(queries, start=1):
            user = getname(query)
            token = get(user.get('id'))
            print_(f"===== Account {index} | {user.get('username')} =====")
            if token == None:
                token = getlogin(query).get('token')
                save(user.get('id'), token)
                time.sleep(2)
            data = getdata(token)
            if data is not None:
                data_init = init(token)
                if data_init is not None:
                    referralData = data_init.get('referralData',{})
                    balance = referralData.get('balance','0')
                    print_(f"Balance : {round(balance)}")
                    total_point += float(balance)
                isDailyRewardClaimed = data.get('isDailyRewardClaimed', True)
                if isDailyRewardClaimed:
                    print_(f"User {user.get('username')} has already claimed today's reward.")
                else:
                    data_checkin = checkin(token)
                    if data_checkin is not None:
                        print_('reward daily    : ' + str(data_checkin['dailyReward']))
                        print_('total login day :' + str(data_checkin['totalDays']))
                        print_('daily reward claimed!')
            time.sleep(2)
            getfarm(token)
            time.sleep(2)
            data_diamond = diamond(token)
            if data_diamond is not None:
                jsonsettings =  data_diamond['settings']
                jsonstate =  data_diamond['state']
                jsondiamondid =  data_diamond['diamondNumber']
                jsontotalreward =  jsonsettings['totalReward']
                if jsonstate == 'available':
                    time.sleep(2)
                    data_complete = complete(token, jsondiamondid)
                    if data_complete is not None:
                        print_('reward diamond   : ' + str(jsontotalreward))
                elif jsonstate == 'unavailable':
                    print_('asteroid unavailable yet!')
                else:
                    print_('asteroid crushed! waiting next round..')
            print_("--- TASK ---")
            if status_task == 'y':
                data_task = gettask(token)
                if data_task is not None:
                    task_list = data_task.get('tasks', [])
                    for item in task_list: 
                        if item['status'] == 'available':
                            id = item.get('id')
                            slug = item.get('slug')                          
                            print_(f'task {slug} started!')
                            data_task = start_task(token, id)
                            time.sleep(2)
                            if data_task is not None:
                                print_(f"task {slug} {data_task.get('status')}")
                        elif item['status'] == 'verified':
                            id = item.get('id')
                            slug = item.get('slug') 
                            rewardAmount = item.get('rewardAmount')
                            data_task = claim_task(token, id)
                            time.sleep(2)
                            if data_task is not None:
                                if data_task.get('status') == 'completed':
                                    print_(f"task {slug} done, reward {rewardAmount} points")
        print_("=============================================")
        print_(f"Total user : {sum} | Total Point : {round(total_point)} ")
        print_("=============================================")
        end_time = time.time()
        total_time = delay - (end_time-start_time)
        if total_time >= 0:
            printdelay(total_time)
            time.sleep(total_time)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()


