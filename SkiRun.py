from actioncable.connection import Connection
from actioncable.subscription import Subscription
import requests
import time
import datetime as dt
import pytz as pz
import re
import os

"""
R. Holley 2021/02/18
There are many print() functions throughout that I have commented out, but that were very useful to me when testing.
I've left some of them in for others to uncomment as desired.

The credentials file is not included as it is specific to my RC account.
To run this code for yourself, you will need to register an app at recurse.rctogether.com/apps

For testing new code in the Python console, I use keyring to call my credentials
For long-term running, I use command line summon -p keyring.py python SkiRun.py to enter the env variables ID and SEC
Supply your ID and secret however you want
"""

ID = os.getenv('ID')
SEC = os.getenv('SEC')
# import keyring
#
# ID = keyring.get_password('summon', 'VIRTUAL_APP_ID')
# SEC = keyring.get_password('summon', 'VIRTUAL_APP_SEC')

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

lodge_id = None
note_id = None
lodge_notes = None
lodge_response = {
    "no": {
        "message": "What kind of manners is that? These tickets are free, you know!"
    },
    "yes": {
        "message": "Enjoy the slopes!"
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

ski_message = {
    "message": "The powder is great today!"
}


def make_notes(bot_id):
    global lodge_notes
    lodge_notes = {
        "open": {
            "bot_id": bot_id,
            "note": {
                "note_text": "You can ask @**RC Lodge** (politely) for a lift ticket.\
                PM @**Rebecca Holley on Zulip if it isn't working."
            }
        },
        "close": {
            "bot_id": bot_id,
            "note": {
                "note_text": "The lodge is currently closed. You can ask @**Rebecca Holley** to run this bot. :)"
            }
        }
    }
    return lodge_notes


def init_lodge():
    r = requests.post(url=f"https://recurse.rctogether.com/api/bots?app_id={ID}&app_secret={SEC}", json=ski_lodge)
    if r.status_code == 200:
        print("Finished building RC Lodge.")
    l_id = get_bot("RC Lodge", "id")
    # print(["bot id from init_lodge: ", l_id])
    global lodge_notes
    lodge_notes = make_notes(l_id)
    r = requests.post(url=f"https://recurse.rctogether.com/api/notes?app_id={ID}&app_secret={SEC}",
                      json=lodge_notes['open'])
    return l_id


def set_lodge(tag: str, n_id: int):
    global lodge_notes
    m = requests.patch(url=f"https://recurse.rctogether.com/api/notes/{n_id}?app_id={ID}&app_secret={SEC}",
                       json=lodge_notes[tag])
    return m


def close_lodge():
    if get_bot("Skier1"):
        skier_id = get_bot("Skier1", "id")
        d = requests.delete(url=f"https://recurse.rctogether.com/api/bots/{skier_id}?app_id={ID}&app_secret={SEC}")
    global note_id
    m = set_lodge('close', note_id)
    if m.status_code == 200:
        print("Lodge currently closed.")
        sub.remove()
        con.disconnect()


def init_skier(skier: str):
    # lodge_id = get_bot("RC Lodge", "id")
    global note_id
    chairlift = all_skiers[skier]
    r = requests.post(url=f'https://recurse.rctogether.com/api/bots?app_id={ID}&app_secret={SEC}', json=chairlift)
    if r.status_code == 200:
        skier_info = get_bot(skier)
        ski_id = skier_info['id']
        ms = requests.patch(url=f"https://recurse.rctogether.com/api/bots/{ski_id}?app_id={ID}&app_secret={SEC}",
                            json=ski_message)
        runs = 0
        while runs < 5:
            ski_down(skier_info, ski_id)
            runs += 1
        d = requests.delete(url=f"https://recurse.rctogether.com/api/bots/{ski_id}?app_id={ID}&app_secret={SEC}")
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


def get_bot(bot_name: str, field: str = None):
    try:
        g = requests.get(url=f"https://recurse.rctogether.com/api/bots?app_id={ID}&app_secret={SEC}")
        if field:
            bot = list(filter(lambda x: x['name'] == bot_name, g.json()))[0][field]
        else:
            bot = list(filter(lambda x: x['name'] == bot_name, g.json()))[0]
    except IndexError:
        bot = False
    return bot


def get_note(world_mess):
    notes = list(filter(lambda x: x['type'] == 'Note' and 'updated_by' in x.keys(), world_mess['payload']['entities']))
    my_note = list(filter(lambda x: x['updated_by']['id'] == lodge_id, notes))[0]
    global note_id
    note_id = list(filter(lambda x: x['updated_by']['id'] == lodge_id, notes))[0]['id']
    return my_note


def ask_lodge(text):
    print("ask_lodge")
    global lodge_id
    if ticket_please(text) == 2:
        lodge_says = requests.patch(url=f"https://recurse.rctogether.com/api/bots/{lodge_id}?app_id={ID}&app_secret={SEC}",
                                    json=lodge_response['yes'])
        print(["lodge_says ", lodge_says.status_code])
        init_skier('Skier1')
        # init_skier('Skier2')
    elif ticket_please(text) == 1:
        lodge_says = requests.patch(url=f"https://recurse.rctogether.com/api/bots/{lodge_id}?app_id={ID}&app_secret={SEC}",
                                    json=lodge_response['no'])
        print(["lodge_says ", lodge_says.status_code])
    if summertime(text):
        close_lodge()
    if bye(text):
        dn = requests.delete(
            url=f"https://recurse.rctogether.com/api/notes/{note_id}?bot_id={lodge_id}&app_id={ID}&app_secret={SEC}")
        dl = requests.delete(
            url=f"https://recurse.rctogether.com/api/bots/{lodge_id}?app_id={ID}&app_secret={SEC}")
        print(dl.status_code)


ticket = re.compile("ticket", flags=re.IGNORECASE)
please = re.compile("please", flags=re.IGNORECASE)
summer = re.compile("summer", flags=re.IGNORECASE)
goodbye = re.compile("goodbye", flags=re.IGNORECASE)


def ticket_please(text: str) -> int:
    ask = []
    for i in [ticket, please]:
        ask.append(int(bool(i.search(text))))
    print(ask)
    print(sum(ask))
    return sum(ask)


def summertime(text: str) -> bool:
    return bool(summer.search(text))


def bye(text: str) -> bool:
    return bool(goodbye.search(text))


# here is where the connection starts
con = Connection(origin='https://recurse.rctogether.com',
                 url=f'wss://recurse.rctogether.com/cable?app_id={ID}&app_secret={SEC}')
con.connect()
while not con.connected:
    time.sleep(0.5)

sub = Subscription(con, identifier={"channel": "ApiChannel"})


def sub_on_receive(message):
    global lodge_id
    global note_id
    global lodge_notes
    if message['type'] == "world":
        print("New message of type \"world\"")
        bots = list(filter(lambda x: x['type'] == 'Bot', message['payload']['entities']))
        exist_lodge = list(filter(lambda x: x['name'] == 'RC Lodge', bots))
        if exist_lodge:
            lodge_id = get_bot("RC Lodge", field="id")
            print(lodge_id)
            note_id = get_note(message)['id']
            print(note_id)
            lodge_notes = make_notes(lodge_id)
            print(lodge_notes['open'])
        else:
            print("There is currently no lodge in Virtual RC!")
            lodge_id = init_lodge()
            print(["init completed, ", lodge_id])
            sub.remove()
            time.sleep(0.5)
            sub.create()

    while globals()['lodge_id'] is None:
        print("Err: no lodge_id. Waiting for world message")
        time.sleep(3)

    if message['type'] == "entity":
        if message['payload']['id'] == 25877:
            print(message['payload'])
        mess = message['payload']['message']
        now = pz.timezone('EST').localize(dt.datetime.now())
        if lodge_id in mess['mentioned_agent_ids']:
            stamp = pz.timezone('UTC').localize(dt.datetime.strptime(mess['sent_at'], "%Y-%m-%dT%H:%M:%SZ"))
            dif = (now - stamp).total_seconds()
            if dif < 2:
                ask_lodge(mess['text'])


sub.on_receive(callback=sub_on_receive)
sub.create()
while con.connected:
    time.sleep(1)
