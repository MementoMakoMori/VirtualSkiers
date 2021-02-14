from actioncable.connection import Connection
from actioncable.subscription import Subscription
# for Virtual RC, you don't need the Message object

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
sub = Subscription(con, identifier={"channel":"ApiChannel"})

# this function allows you to decide what to do with message contents
def sub_on_receive(message):
    print("New message received of type {}!".format(message['type']))
    # here you may want to call other functions
    # that send HTTP requests to https://recurse.rctogether.com/api based on the message input

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