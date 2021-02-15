from actioncable.connection import Connection
from actioncable.subscription import Subscription
import requests
import time
import datetime as dt
import pytz as pz
import re
import json

"""
R. Holley 2021/02/13
There are many print() functions throughout that I have commented out, but that were very useful to me when testing.
I've left them in for others to uncomment as desired.


The credentials file is not included as it is specific to my RC account.
To run this code for yourself, you will need to register an app at recurse.rctogether.com/apps
"""

app_cred = json.load(open("app_credentials.json", "r"))
ID = app_cred['id']
SEC = app_cred['secret']

# the x-y coordinates are hard coded and will need to change if Virtual RC map changes
ski_lodge = {
    "bot": {
        "name": "RC Lodge",
        "emoji": "🏠",
        "x": 45,
        "y": 109,
        "direction": "left",
        "can_be_mentioned": True,
    }
}

lodge_message = {
    "open": {
        "bot_id": lodge_id,
        "note": {
            "note_text": "You can ask @**RC Lodge** (politely) for a lift ticket."
        }
    },
    "ski": {
        "bot_id": lodge_id,
        "note": {
        "note_text": "The powder is great today!"
        }
    },
    "close": {
        "bot_id": lodge_id,
        "note": {
            "note_text": "The lodge is currently closed. You can ask @**Rebecca Holley** to run this bot. :)"
        }
    }
}

all_skiers = {
    "Skier1": {
        "bot": {
            "name": "Skier1",
            "emoji": "⛷️",
            "x": 54,
            "y": 103,
            "direction": "down",
            "can_be_mentioned": False
        }
    },
    "Skier2": {
        "bot": {
            "name": "Skier1",
            "emoji": "⛷️",
            "x": 55,
            "y": 105,
            "direction": "down",
            "can_be_mentioned": False
        }
    }
}


def init_lodge():
    r = requests.post(url=f"https://recurse.rctogether.com/api/bots?app_id={ID}&app_secret={SEC}", json=ski_lodge)
    if r.status_code == 200:
        print("Finished building RC Lodge.")
        l_id = get_bot("RC Lodge", "id")
        # m = set_lodge('open', l_id)
        # if m.status_code == 200:
        #     print("RC Lodge is ready for the season!")
    r = requests.post(url=f"https://recurse.rctogether.com/api/notes?app_id={ID}&app_secret={SEC}", json = lodge_message['open'])
    return l_id


def set_lodge(tag: str, n_id: int):
    m = requests.patch(url=f"https://recurse.rctogether.com/api/notes/{n_id}?app_id={ID}&app_secret={SEC}",
                       json=lodge_message[tag])
    return m


def close_lodge():
    print("It's too warm for snow now.")
    if get_bot("Skier1"):
        skier_id = get_bot("Skier1", "id")
        d = requests.delete(url=f"https://recurse.rctogether.com/api/bots/{skier_id}?app_id={ID}&app_secret={SEC}")
    m = set_lodge('close', lodge_id)
    print("Close message sent")
    if m.status_code == 200:
        # print("Lodge currently closed.")
        sub.remove()
        con.disconnect()


def init_skier(skier: str):
    set_lodge('ski', lodge_id)
    chairlift = all_skiers[skier]
    r = requests.post(url=f'https://recurse.rctogether.com/api/bots?app_id={ID}&app_secret={SEC}', json=chairlift)
    if r.status_code == 200:
        skier_info = get_bot(skier)
        ski_id = skier_info['id']
        runs = 0
        while runs < 5:
            ski_down(skier_info, ski_id)
            runs += 1
        d = requests.delete(url=f"https://recurse.rctogether.com/api/bots/{ski_id}?app_id={ID}&app_secret={SEC}")
        m = set_lodge('open', lodge_id)
        # if d.status_code == 200:
        #     print("Done skiing for now.")
        #     pass


def ski_down(skier: dict, b_id: str):
    slope = skier['pos']['y']
    carve = skier['pos']['x']
    while slope < 109:
        wheee = {'bot': {'x': carve - 1, 'y': slope + 1}}
        r = requests.patch(url=f"https://recurse.rctogether.com/api/bots/{b_id}?app_id={ID}&app_secret={SEC}",
                           json=wheee)
        slope += 1
        carve -= 1
        time.sleep(1)


def get_bot(bot_name: str, field: str=None):
    try:
        g = requests.get(url=f"https://recurse.rctogether.com/api/bots?app_id={ID}&app_secret={SEC}")
        if field:
            bot = list(filter(lambda x: x['name'] == bot_name, g.json()))[0][field]
        else:
            bot = list(filter(lambda x: x['name'] == bot_name, g.json()))[0]
    except:
        bot = False
    return bot

def get_note(world_mess):
    notes = list(filter(lambda x: x['type'] == 'Notes' and 'updated_by' in x.keys(), world_mess['payload']['entities']))
    n_id = list(filter(lambda x: x['updated_by']['id'] == lodge_id, notes))[0]['id']
    return n_id



ticket = re.compile("ticket", flags=re.IGNORECASE)
please = re.compile("please", flags=re.IGNORECASE)
summer = re.compile("summer", flags=re.IGNORECASE)

def ticket_please(text: str) -> bool:
    return bool(ticket.search(text) and please.search(text))


def summertime(text: str) -> bool:
    return bool(summer.search(text))


# here is where the connection starts
con = Connection(origin='https://recurse.rctogether.com',
                 url=f'wss://recurse.rctogether.com/cable?app_id={ID}&app_secret={SEC}')
con.connect()
while not con.connected:
    time.sleep(0.5)

sub = Subscription(con, identifier={"channel": "ApiChannel"})

lodge_id = None


def sub_on_receive(message):

    if message['type'] == "world":

        print("New message of type \"world\"")
        bots = list(filter(lambda x: x['type'] == 'Bot', message['payload']['entities']))
        exist_lodge = list(filter(lambda x: x['name'] == 'RC Lodge', bots))
        if exist_lodge:
            global lodge_id
            lodge_id = get_bot("RC Lodge", field="id")
            global note_id
            note_id = get_note(message)
        else:
            print("There is currently no lodge in Virtual RC!")
            global lodge_id
            lodge_id = init_lodge()
            sub.remove()
            sub.create()


    if message['type'] == "entity":
        mess = message['payload']['message']
        now = pz.timezone('EST').localize(dt.datetime.now())
        stamp = pz.timezone('UTC').localize(dt.datetime.strptime(mess['sent_at'], "%Y-%m-%dT%H:%M:%SZ"))
        dif = (now - stamp).total_seconds()
        if lodge_id in mess['mentioned_agent_ids'] and dif < 2:
            if ticket_please(mess['text']):
                init_skier('Skier1')
                # init_skier('Skier2')
            if summertime(mess['text']):
                close_lodge()


sub.on_receive(callback=sub_on_receive)
sub.remove()
sub.create()
