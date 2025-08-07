import requests
from time import time, sleep
from threading import Thread, Lock
from colorama import Fore, init
import os
import re
from itertools import cycle
import json

Tele_webhook = ''  #needs to end with '&text=' for webhook message to be inserted

with open("./Accounts/test.txt", "w") as file:
    file.write("test")

game = 1
delete_timer = 50000
if game == 1:
    gname = "Fortnite"
    sc = "93ac0100-efec-488c-af85-e5850ff4b5bd"
elif game == 2:
    gname = "Rocket League"
    sc = "90c40100-9123-47d6-bc6b-35d3214e91ac"
elif game == 3:
    gname = "Roblox"
    sc = "bab50100-e49a-4ce8-b16f-918d1465f7bc"

with open("./Accounts/FullTokens.txt", "r") as m:
    lines = [line.strip() for line in m.readlines() if line.strip()] 
    
    if lines:  
        ownerauth = lines[-1]  
        messageauthslist = lines[:-1]  
        howmany = len(messageauthslist)
        
init()

TR = f"[{Fore.MAGENTA}TR{Fore.RESET}]"
INFO = f"[{Fore.YELLOW}?{Fore.RESET}]"
CLAIMED = f"[{Fore.GREEN}+{Fore.RESET}]"
MISSED = f"[{Fore.RED}-{Fore.RESET}]"

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

HEADERSREFRESH2 = {
    "Accept-Language": "en-US",
    "X-UserAgent": "Android/190914000 G011A.AndroidPhone",
    "MS-CV": "OGgg1Psvnqk5LyBE.41",
    "Authorization": "",
    "X-Xbl-Contract-Version": "3",
    "X-Xbl-Correlation-Id": "c2c1cc07-cb0a-4823-b584-e40be13762cc",
    "Content-Type": "application/json; charset=UTF-8",
    "Content-Length": "250",
    "Host": "peoplehub.xboxlive.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/3.12.1"
}

HEADERSMESSAGE = {
    "Accept-Language": "en-US",
    "X-UserAgent": "Android/190914000 G011A.AndroidPhone",
    "MS-CV": "OGgg1Psvnqk5LyBE.41",
    "Authorization": "",  # This will be set dynamically with the rotated token
    "Content-Type": "application/json; charset=UTF-8",
    "Host": "xblmessaging.xboxlive.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/3.12.1"
}

HEADERSPOST = {
    "Accept-Language": "en-US",
    "X-UserAgent": "Android/190914000 G011A.AndroidPhone",
    "Authorization": ownerauth,
    "X-Xbl-Contract-Version": "3",
    "Content-Type": "application/json; charset=UTF-8",
    "Content-Length": "250",
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

proxies2 = {
    'http': 'can add proxy urls here'
}

g = requests.get('https://accounts.xboxlive.com/users/current/profile', headers=HEADERSPOST)
gdata = g.json()
xuid = (gdata.get('ownerXuid', 0))

payloadPost = {"postText":"Insert your post text here","postType":"Text","timelines":[{"timelineType":"User","timelineOwner":str(xuid)}]}
r = requests.post('https://userposts.xboxlive.com/users/me/posts', headers=HEADERSPOST, json=payloadPost)
#payloadPost = {"postText":":"Text","timelines":[{"timelineType":"User","timelineOwner":"teste328484}]}
rdata = r.json()
userpost = rdata["timelines"][0].get("timelineUri")

PAYLOADMESSAGE = {"parts": [{"contentType": "feedItem", "version": 0, "locator": userpost}]}


pattern = re.compile(r'\b\d{16}\b')

def findXuids(obj):
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

    def stop_all(self):
        """Stops all running threads safely."""
        d = requests.delete(f'https://{userpost}', headers=HEADERSDELETE)
        if d.status_code == 200:
            msg = 'Successfully deleted post bc of no owner or post.'
            requests.post(f'{Tele_webhook}{msg}')
        else:
            msg = f'Unsuccessful shutdown and deletion bc of post or owner, status code: {d.status_code}'
            requests.post(f'{Tele_webhook}{msg}')
        with self.lock:
            if self.running:  
                print("Stopping all threads and exiting...")
                self.running = False  
                if os.path.exists("./Accounts/done.txt"):
                    os.remove("./Accounts/done.txt")

                    print("Python finished processing. Restarting Go program.")
                os._exit(0)  


    def print(self, text):
        with self.lock:
            print(text)

    def rotate_token(self):
        return next(self.token_cycle)
    
    def get_stats(self):
        statsurl = f'https://comments.xboxlive.com/{userpost}/comments?maxItems=10'
        r = requests.get(statsurl, headers=HEADERSDELETE)
        if r.status_code in [200,202,429]:
            response=r.json()

            comments = response.get('comments', [])
            self.like_count = response.get('likeCount', 0)
            #comment_count = response.get('commentCount', 0)

            for comment in comments:
                gamertag = comment.get('gamertag')
                text = comment.get('text')
                message = f'({gamertag}: {text}\n\n - Fortnite Instance | Likes: {self.like_count} | Bans: {self.bans}/{howmany})'
                path = comment.get('path')

                delUrl = f'https://{path}'
                d = requests.delete(delUrl, headers=HEADERSDELETE)
                if d.status_code == 200:
                    self.commentsdeleted+=1
                    requests.post(f'{Tele_webhook}{message}')
                else:
                    pass
        else:
            msg='FN post deleted for lack of owner or post'
            requests.post(f'{Tele_webhook}{msg}')
            self.stop_all()

        #print(f"successfully deleted {deleted} comments!")

    def delete_post(self):
        
        d = requests.delete(f'https://{userpost}', headers=HEADERSDELETE)
        if d.status_code == 200:
            msg = 'Successfully deleted post.'
            requests.post(f'{Tele_webhook}{msg}')
        else:
            msg = f'Unsuccessful shutdown and deletion, status code: {d.status_code}'
            requests.post(f'{Tele_webhook}{msg}')
        self.stop_all()


    def make_request(self):
        while self.running:
            try:
                response = requests.post(self.url, headers=HEADERSREFRESH, json=PAYLOADREFRESH)


                if response.status_code == 200:
                    self.refreshes += 1
                    data = response.json()
                    xuidList = findXuids(data)

                    #makeall
                    for xuid in xuidList:
                        with open('xuids.txt', 'r+') as w:
                            content = w.read()

                            storage = []
                            token = self.rotate_token()
                            HEADERSREFRESH2["Authorization"] = token
                            f = requests.get(f'https://peoplehub.xboxlive.com/users/xuid({xuid})/people/social/decoration/multiplayersummary,preferredcolor', headers=HEADERSREFRESH2)
                            if f.status_code == 200:
                                
                                fdata = f.json()
                                people_data = fdata.get('people', [])
                                for person in people_data:
                                    if person.get('presenceState') == "Online" and person.get('presenceText') and 'fortnite' in person.get('presenceText').lower():
                                        #print(person.get('presenceText'))
                                        lol1 = (person.get('xuid'))
                                        storage.append(lol1)

                                        
                                        if lol1 not in content:
                                            token = self.rotate_token()
                                            HEADERSMESSAGE["Authorization"] = token
                                            msg = requests.post(f'https://xblmessaging.xboxlive.com/network/Xbox/users/me/conversations/users/xuid({lol1})', headers=HEADERSMESSAGE, json=PAYLOADMESSAGE)
                                            w.write(lol1 + "\n")
                                            if msg.status_code == 200:
                                                    self.messages += 1
                                                    #sleep(0.3)
                                                    self.get_stats()
                                            elif msg.status_code == 429:
                                                    sleep(4)
                                                    self.messagerl += 1
                                            elif msg.status_code == 403 or msg.status_code == 401:
                                                    self.bans += 1
                                                    #print(f"token {token} is banned or locked, removing.")
                                                    messageauthslist.remove(token)
                                                    self.token_cycle = cycle(messageauthslist)
                                                    if howmany/self.bans <= 2:
                                                        d = requests.delete(f'https://{userpost}', headers=HEADERSDELETE)
                                                        if d.status_code == 200:
                                                            msg = f'Successfully deleted fn post early (Screen 407) - Likes: {self.like_count}'
                                                            requests.post(f'{Tele_webhook}{msg}')
                                                        else:
                                                            msg = f'Unsuccessful (early) fn shutdown and deletion, status code: {d.status_code}'
                                                            requests.post(f'{Tele_webhook}{msg}')
                                                        self.stop_all()
                                            else:
                                                    pass
                                                    #sleep(2)
                                        else: 
                                            #print("avoiding this xuid")
                                            pass
                            else:
                                sleep(4)

            #print(xx)
                            for xuid in storage:
                                token = self.rotate_token()
                                HEADERSREFRESH2["Authorization"] = token
                                ff = requests.get(f'https://peoplehub.xboxlive.com/users/xuid({xuid})/people/social/decoration/multiplayersummary,preferredcolor', headers=HEADERSREFRESH2)
                                if ff.status_code == 200:
                                    ffdata = ff.json()

                                    people_data = ffdata.get('people', [])
                                    for person in people_data:
                                        if person.get('presenceState') == "Online" and person.get('presenceText') and 'fortnite' in person.get('presenceText').lower():
                                        #if person.get('presenceState') == "Online":
                                            #print(person.get('presenceText'))
                                            lol = (person.get('xuid'))

                                            if lol not in content:
                                                token = self.rotate_token()
                                                HEADERSMESSAGE["Authorization"] = token
                                                msg = requests.post(f'https://xblmessaging.xboxlive.com/network/Xbox/users/me/conversations/users/xuid({lol})', headers=HEADERSMESSAGE, json=PAYLOADMESSAGE)

                                                if msg.status_code == 200:
                                                    self.messages += 1
                                                    #sleep(0.5)
                                                    self.get_stats()
                                                elif msg.status_code == 429:
                                                    sleep(4)
                                                    self.messagerl += 1
                                                elif msg.status_code == 403 or msg.status_code == 401:
                                                    self.bans += 1
                                                    #print(f"token {token} is banned or locked, removing.")
                                                    messageauthslist.remove(token)
                                                    self.token_cycle = cycle(messageauthslist)
                                                    if howmany/self.bans <= 2:
                                                        d = requests.delete(f'https://{userpost}', headers=HEADERSDELETE)
                                                        if d.status_code == 200:
                                                            msg = f'Successfully deleted fn post (early) - Likes: {self.like_count}'
                                                            requests.post(f'{Tele_webhook}{msg}')
                                                        else:
                                                            msg = f'Unsuccessful fn (early) shutdown and deletion, status code: {d.status_code}'
                                                            requests.post(f'{Tele_webhook}{msg}')
                                                        self.stop_all()
                                                else:
                                                    #sleep(2)
                                    #self.print(f"{MISSED} Unexpected status code while messaging: {msg.status_code}")
                                            
                                                    w.write(lol + "\n")
                                            else: 
                                                #print("avoiding this xuid")
                                                pass
                            storage.clear()
                            
                elif response.status_code == 429:
                    self.print(f"{MISSED} Rate limited while refreshing.")
                else:
                    sleep(1)
                    #self.print(f"{INFO} Unexpected status code while refreshing: {response.status_code}")
                sleep(1)
            except Exception as e:
                sleep(5)


    def start_threads(self):
        #self.print(f"{INFO} Starting {self.threads} threads.")
        thread_list = []
        for _ in range(self.threads):
            thread = Thread(target=self.make_request)
            thread.start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join()

    def stop(self):
        self.running = False
        self.print(f"{INFO} Stopping threads...")
        self.stop_all()

    def tracker(self):
        while self.running:
            sleep(0.5)
            with self.lock:
                #test = '\n'
                print(
                f"\rGame: {gname} | "
                f"Tokens: #{self.tokensnum} | "
                f"Sent: [{Fore.GREEN}{self.messages}{Fore.RESET}] | "
                f"RL: [{Fore.RED}{self.messagerl}{Fore.RESET}] | "
                f"Refreshed: #{self.refreshes} | ",
                #f"Already Messaged: {self.messaged} | "
                f"Comments Removed: {self.commentsdeleted} | "
                f"Post Likes: {self.like_count} | "
                f"Bans: {self.bans}",
                end='', flush=True
            )

                
    def delete_post(self):
        sleep(delete_timer)
        d = requests.delete(f'https://{userpost}', headers=HEADERSDELETE)
        if d.status_code == 200:
            msg = 'Successfully deleted post.'
            requests.post(f'{Tele_webhook}{msg}')
        else:
            msg = f'Unsuccessful shutdown and deletion, status code: {d.status_code}'
            requests.post(f'{Tele_webhook}{msg}')
        self.stop_all()


if __name__ == "__main__":
    print(f"""\
                   _  __ ____  __            
                  | |/ // __ )/ /   ____ ___ 
                  |   // __  / /   / __ `__ |
                 /   |/ /_/ / /___/ / / / / / 
                /_/|_/_____/_____/_/ /_/ /_/ 
                                               
            
    [{Fore.MAGENTA}github old version demo | dont try to use this :){Fore.RESET}]
          
          """)
    requester = Requester("https://sessiondirectory.xboxlive.com/handles/query?include=relatedInfo,roleInfo,activityInfo", 1)
    


    try:
        tracker_thread = Thread(target=requester.tracker)
        tracker_thread.start()
        delete_thread = Thread(target=requester.delete_post)
        delete_thread.start()
        #msg = '- Launched Messages -'
        #requests.post(f'{Tele_webhook}{msg}')
        requester.start_threads()

    except KeyboardInterrupt:
        requester.stop()

