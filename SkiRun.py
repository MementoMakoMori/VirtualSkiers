from actioncable.connection import Connection
from actioncable.subscription import Subscription
import requests
import time
import datetime as dt
import pytz as pz
from skilodge import SkiLodge

"""
R. Holley 2021/02/22
There are many print() functions throughout these files that I have commented out, but that were very useful to me 
when testing. I've left some of them in for others to uncomment as desired.

The credentials file is not included as it is specific to my RC account.
To run this code for yourself, you will need to register an app at recurse.rctogether.com/apps

For testing new code in the Python console, I use keyring to call my credentials
For long-term running, I use command line summon -p keyring.py python SkiRun.py to enter the env variables ID and SEC
Supply your ID and secret however you want
"""


def get_bot(bot_name: str, field: str = None, app_id: str = None, app_sec: str = None):
    if not app_id:
        app_id = ID
    if not app_sec:
        app_sec = SEC
    try:
        g = requests.get(url=f"https://recurse.rctogether.com/api/bots?app_id={app_id}&app_secret={app_sec}")
        if field:
            bot = list(filter(lambda x: x['name'] == bot_name, g.json()))[0][field]
        else:
            bot = list(filter(lambda x: x['name'] == bot_name, g.json()))[0]
    except IndexError:
        bot = False
    return bot


def get_note(world_entities):
    if not lodge.id:
        print("Error: no lodge id")
    else:
        notes = list(filter(lambda x: x['type'] == 'Note' and 'updated_by' in x.keys(), world_entities))
        n_id = list(filter(lambda x: x['updated_by']['id'] == lodge.id, notes))
        if not n_id:
            print("No note found! Will try to make one and get a new world message.")
            lodge.new_note()
            sub.remove()
            sub.create()
        return n_id[0]['id']


def sub_on_receive(message):
    global lodge
    if message['type'] == "world":
        print("New message of type \"world\"")
        bots = list(filter(lambda x: x['type'] == 'Bot', message['payload']['entities']))
        exist_lodge = list(filter(lambda x: x['name'] == lodge.name, bots))
        if exist_lodge:
            lodge.id = get_bot(lodge.name, 'id')
            lodge.make_notes()
            lodge.note_id = get_note(message['payload']['entities'])
        else:
            print("There is currently no lodge in Virtual RC!")
            lodge.new_lodge()
            # print(["init completed, ", lodge.id])

    if message['type'] == "entity":
        now = pz.timezone('EST').localize(dt.datetime.now())
        mess = message['payload']['message']
        if lodge.id in mess['mentioned_agent_ids']:
            stamp = pz.timezone('UTC').localize(dt.datetime.strptime(mess['sent_at'], "%Y-%m-%dT%H:%M:%SZ"))
            dif = (now - stamp).total_seconds()
            if dif < 2:
                lodge.ask_lodge(mess['text'])


if __name__ == "__main__":
    # import os
    # ID = os.getenv('ID')
    # SEC = os.getenv('SEC')
    import keyring
    ID = keyring.get_password('summon', 'VIRTUAL_APP_ID')
    SEC = keyring.get_password('summon', 'VIRTUAL_APP_SEC')
    lodge = SkiLodge(app_id=ID, app_sec=SEC, name="RC Lodge")
    con = Connection(origin='https://recurse.rctogether.com',
                     url=f'wss://recurse.rctogether.com/cable?app_id={ID}&app_secret={SEC}')
    con.connect()
    while not con.connected:
        time.sleep(0.5)
    sub = Subscription(con, identifier={"channel": "ApiChannel"})
    sub.on_receive(callback=sub_on_receive)
    sub.create()

    time.sleep(10)
    while con.connected:
        time.sleep(1)
