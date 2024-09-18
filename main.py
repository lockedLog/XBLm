import requests
from time import time, sleep
from threading import Thread, Lock
from colorama import Fore, init
from os import system, name
import os
import re
from itertools import cycle
import json
import sys


def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

while True:
        game = int(input("1. Fortnite \n2. COD\n3. Rocket League\n4. Fall Guys\n5. Roblox\n\n"))
        if game == 1:
            gname = "Fortnite"
            sc = "93ac0100-efec-488c-af85-e5850ff4b5bd"
            break
        elif game == 2:
            gname = "COD"
            sc = "90c40100-9123-47d6-bc6b-35d3214e91ac"
            break
        elif game == 3:
            gname = "Rocket League"
            sc = "90c40100-9123-47d6-bc6b-35d3214e91ac"
            break
        elif game == 4:
            gname = "Fall Guys"
            sc = "00000000-0000-0000-0000-00007805512b"
            break
        elif game == 5:
            gname = "Roblox"
            sc = "bab50100-e49a-4ce8-b16f-918d1465f7bc"
            break
        else: 
            print('Try again')


with open("messagers.txt", "r") as m:
    messageauthslist = [line.strip() for line in m.readlines()]
    howmany = len(messageauthslist)

with open("owner.txt", "r") as o:
    ownerauth = o.read()

with open("config.json", "r") as j:
        dataconfig = json.load(j)
        timer = dataconfig['runtimeSeconds']
        userpost = dataconfig['postLink']

init()

error = f"[{Fore.YELLOW}?{Fore.RESET}]"
plus = f"[{Fore.GREEN}+{Fore.RESET}]"
minus = f"[{Fore.RED}-{Fore.RESET}]"

HEADERSDELETE = {
    "Accept-Language": "en-US",
    "X-UserAgent": "Android/190914000 G011A.AndroidPhone",
    "MS-CV": "OGgg1Psvnqk5LyBE.41",
    "Content-type": "application/json",
    "Authorization": ownerauth,
    "Content-Length": "0",
    "Host": "userposts.xboxlive.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/3.12.1"
}

HEADERSREFRESH = {
    "Accept-Language": "en-US",
    "X-UserAgent": "Android/190914000 G011A.AndroidPhone",
    "MS-CV": "OGgg1Psvnqk5LyBE.41",
    "Authorization": ownerauth,
    "X-Xbl-Contract-Version": "107",
    "X-Xbl-Correlation-Id": "c2c1cc07-cb0a-4823-b584-e40be13762cc",
    "Content-Type": "application/json; charset=UTF-8",
    "Content-Length": "250",
    "Host": "sessiondirectory.xboxlive.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/3.12.1"
}

HEADERSMESSAGE = {
    "Accept-Language": "en-US",
    "X-UserAgent": "Android/190914000 G011A.AndroidPhone",
    "MS-CV": "OGgg1Psvnqk5LyBE.41",
    "Authorization": "", 
    "Content-Type": "application/json; charset=UTF-8",
    "Host": "xblmessaging.xboxlive.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/3.12.1"
}

PAYLOADREFRESH = {
    "communicatePermissionRequired": True,
    "filter": "session/roles/lfg/confirmed/needs gt 0",
    "followed": False,
    "includeScheduled": True,
    "orderBy": "suggestedLfg desc",
    "scid": sc,
    "templateName": "global(lfg)",
    "type": "search"
}


PAYLOADMESSAGE = {"parts": [{"contentType": "feedItem", "version": 0, "locator": userpost}]}


def findXuids(obj):
    pattern = re.compile(r'\b\d{16}\b')
    results = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            results.extend(findXuids(value))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(findXuids(item))
    elif isinstance(obj, str):
        matches = pattern.findall(obj)
        results.extend(matches)
    return results

class Requester:
    def __init__(self, url, threads):
        self.url = url
        self.threads = threads
        self.messages = 0
        self.messagerl = 0
        self.refreshes = 0
        self.bans = 0
        self.messaged = 0
        self.commentsdeleted = 0
        self.like_count = 0
        self.tokensnum = howmany
        self.running = True
        self.lock = Lock()
        self.token_cycle = cycle(messageauthslist)
        self.tracker_started = False

    def print(self, text):
        with self.lock:
            print(text)

    def rotate_token(self):
        return next(self.token_cycle)
    
    def get_stats(self):
        statsurl = f'https://comments.xboxlive.com/{userpost}/comments?maxItems=200'
        r = requests.get(statsurl, headers=HEADERSDELETE)
        response=r.json()

        comments = response.get('comments', [])
        self.like_count = response.get('likeCount', 0)
        #comment_count = response.get('commentCount', 0)

        for comment in comments:
            gamertag = comment.get('gamertag')
            #text = comment.get('text')
            path = comment.get('path')

            delUrl = f'https://{path}'
            if dataconfig['removeComments'] is True:
                d = requests.delete(delUrl, headers=HEADERSDELETE)
                if d.status_code == 200:
                    self.commentsdeleted+=1
                else:
                    print(f"{error} Error occured while deleting comment from {gamertag}.")
            else: 
                pass
        #print(f"successfully deleted {deleted} comments!")


    def make_request(self):
        while self.running:
            try:
                response = requests.post(self.url, headers=HEADERSREFRESH, json=PAYLOADREFRESH)
                
                if response.status_code == 200:
                    self.refreshes += 1
                    data = response.json()
                    xuidList = findXuids(data)
                    for xuid in xuidList:
                        with open("xuids.txt", "r+") as file:
                            content = file.read()
                            if xuid not in content:
                                token = self.rotate_token()
                                HEADERSMESSAGE["Authorization"] = token
                                msg = requests.post(f'https://xblmessaging.xboxlive.com/network/Xbox/users/me/conversations/users/xuid({xuid})', headers=HEADERSMESSAGE, json=PAYLOADMESSAGE)
                                file.write(xuid + "\n")
                                if msg.status_code == 200:
                                    self.messages += 1
                                    sleep(0.9) #less with more accounts, or more with less than 4 messagers
                                    self.get_stats()
                                elif msg.status_code == 429:
                                    sleep(7)
                                    self.messagerl += 1
                                elif msg.status_code == 403 or msg.status_code == 401:
                                    self.bans += 1
                                    #print(f"token {token} is banned or locked, removing.")
                                    messageauthslist.remove(token)
                                    self.token_cycle = cycle(messageauthslist)
                                else:
                                    sleep(2)
                                    self.print(f"{minus} Unexpected status code while messaging: {msg.status_code}")
                            else:
                                self.messaged += 1
                elif response.status_code == 429:
                    self.print(f"{minus} Rate limited while refreshing.")
                else:
                    sleep(1)
                    self.print(f"{error} Unexpected status code while refreshing: {response.status_code}")
                sleep(1)
            except Exception as e:
                self.print(f"{error} Error: {e}")
                sleep(5)

    def start_threads(self):
        thread_list = []
        for _ in range(self.threads):
            thread = Thread(target=self.make_request)
            thread.start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join()

    def stop(self):
        self.running = False
        self.print(f"{minus} Stopping threads...")

    def tracker(self):
        while self.running:
            sleep(0.5)
            with self.lock:
                print(
                f"\rGame: {gname} | "
                f"Tokens: {self.tokensnum} | "
                f"Sent: [{Fore.GREEN}{self.messages}{Fore.RESET}] | "
                f"RL: [{Fore.RED}{self.messagerl}{Fore.RESET}] | "
                f"Refreshed: #{self.refreshes} | ",
                f"Comments Removed: {self.commentsdeleted} | "
                f"Post Likes: {self.like_count} | "
                f"Bans: {self.bans}",
                end='', flush=True
            )

                
    def delete_post(self):
        sleep(timer)
        d = requests.delete(f'https://{userpost}', headers=HEADERSDELETE)
        if d.status_code == 200:
            sys.exit(f'Successfully deleted post.')
        else:
            sys.exit(f'Unsuccessful shutdown and deletion, status code: {d.status_code}')


if __name__ == "__main__":
    with open("config.json", "r") as jsonfile:
        data = json.load(jsonfile)
        if data['deletePost'] in [True, False] and data['removeComments'] in [True, False] and isinstance(data['runtimeSeconds'], int) and isinstance(data['postLink'], str):
            print('Configuration successfully set')
            sleep(2)
        else:
            sys.exit("Error reading config file\n\nFormat:\n\nuniqueOnly: true/false,\nremoveComments: true/false,\nruntimeSeconds: integer,\npostLink: string")

        
    clear()

    print(f"""\
                   _  __ ____  __            
                  | |/ // __ )/ /   ____ ___ 
                  |   // __  / /   / __ `__ |
                 /   |/ /_/ / /___/ / / / / / 
                /_/|_/_____/_____/_/ /_/ /_/ 
                                                               

            [{Fore.MAGENTA}github.com/lockedLog{Fore.RESET}]
          
          """)
    requester = Requester("https://sessiondirectory.xboxlive.com/handles/query?include=relatedInfo,roleInfo,activityInfo", 1)
    

    try:
        tracker_thread = Thread(target=requester.tracker)
        tracker_thread.start()
        delete_thread = Thread(target=requester.delete_post)
        if data['deletePost'] is True:
            delete_thread.start()
        else:
            pass
        
        requester.start_threads()


    except KeyboardInterrupt:
        requester.stop()