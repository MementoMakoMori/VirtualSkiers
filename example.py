from actioncable.connection import Connection
from actioncable.subscription import Subscription
import requests
import time

# get these from https://recurse.rctogether.com/apps after making an app
ID = "123"
SEC = "456"

con = Connection(origin='https://recurse.rctogether.com',
                 url=f'wss://recurse.rctogether.com/cable?app_id={ID}&app_secret={SEC}')
con.connect()
# you're connected! but you don't have any messages yet
# check this to make sure you are connected
print(con.connected)

# be careful with your quotation marks!
sub = Subscription(con, identifier={"channel": "ApiChannel"})

# here are some basic examples for building a bot
# this bot will appear in the top-left corner of VirtualRC
bot_info = {
    "bot": {
        "name": "Example Bot",
        "emoji": "😊",
        "x": 5,
        "y": 4,
        "direction": "right",
        "can_be_mentioned": True,
    }
}

bot_message = {
    "message": "Hello, I am a bot run from example.py"
}

# successful requests return status code 200
def init_bot():
    r = requests.post(url=f"https://recurse.rctogether.com/api/bots?app_id={ID}&app_secret={SEC}", json=bot_info)
    print(f"Init status: {r.status_code}")


def get_bot():
    r = requests.get(url=f"https://recurse.rctogether.com/api/bots?app_id={ID}&app_secret={SEC}")
    print(f"get_bot status: {r.status_code}")
    print(r.json())
    # the following assumes you only have one bot
    bot_id = r.json()[0]['id']
    return bot_id


def update_bot():
    b_id = get_bot()
    r = requests.path(url=f"https://recurse.rctogether.com/api/bots/{b_id}?app_id={ID}&app_secret={SEC}", json=bot_message)
    print(f"update_bot status: {r.status_code}")


def delete_bot():
    b_id = get_bot()
    r = requests.delete(url=f"https://recurse.rctogether.com/api/bots/{b_id}?app_id={ID}&app_secret={SEC}")
    print(f"delete status: {r.status_code}")


# this function allows you to decide what to do with message contents
def sub_on_receive(message):
    print("New message received of type {}!".format(message['type']))
    # here you may want to call other functions
    # that send HTTP requests to https://recurse.rctogether.com/api based on the message input

    # the first message you receive will be 'world', which is the status for EVERYTHING in VirtualRC
    # don't print it, it's huge
    if message['type'] == "world":
        init_bot()
        time.sleep(3)
        get_bot()
        time.sleep(3)
        update_bot()
        time.sleep(30)
        delete_bot()

sub.on_receive(callback=sub_on_receive)

# this function sends the "command":"subscribe" message to the ApiChannel
sub.create()
# you should now be receiving messages! if not, check the following
print(sub.state)
# if sub.state is 'pending', you may have downloaded the old version of ActionCableZwei!
# 'subscription_pending' means that your Connection object is not connected (check con.connected)

# this 'unsubscribes' you from the ApiChannel
sub.remove()

# re-subscribing will send you a new 'world' message
sub.create()