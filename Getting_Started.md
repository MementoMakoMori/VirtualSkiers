# So you want to build a Virtual RC Bot
## using ActionCable for Python
### idk why you're not using javascript but here goes nothing
___
Rebecca Holley

I wrote this in about 10 minutes so I apologize for typos!

### 0. (optional) Clone this Repo
Assuming you have opened a terminal and navigated to your preferred folder/environment.
If you are totally new to Python than having the example.py file to fill in will probably be useful.
````commandline
git clone https://github.com/MementoMakoMori/VirtualSkiers.git
````
### 1. Download ActionCable client
You won't need this if you did step 0 and cloned this repo, but if you are working from scratch then here is what you'll need to get started.
```commandline
pip install git+https://github.com/tobiasfeistmantl/python-actioncable-zwei.git&egg=ActionCableZwei
```
Do **not** do what the client repo's README says and just using pip install from Pypi. The version on Pypi has not been updated since 2017 and *it will not work.*
You also do not need the Messages class. I do not know if it has deprecated for ActionCable in general, or if it's just that the VirtualRC setup doesn't use it.
### 2. Register a VirtualRC App
Go to [recurse.rctogether.com/apps](https://recurse.rctogether.com/apps) and create an app! You can change the name later, so don't fret over it.

### 3. Starting coding!
 > This is where the fun begins...
 
The example.py file really has everything you need to get connected, so I'll only note a few things here.
 * There is no console output/printing when you successfully (or unsuccessfully) connect to the API and subscribe to a channel. To check these things, you will have to check attributes of your Connection class object and Subscription class object.
```python
your_connection.connect()
# ...did it work?
your_connection.connected

your_subscription.create()
# if you don't start receiving messages after .create(), check:
your_subscription.state
```
Connection.connected will return True/False; Subscription.state will return one of several strings - if everything works it should return 'subscribed'.
* Get comfortable with JSON! The information you send to VirtualRC and the info you receive will be in the form of json. The examples in [VirtualRC docs](https://docs.rctogether.com/) have basically everything you need on the json front. Mind your quotes and commas!
* REST in Python, imo is way easier than the curl examples in the docs. All you need is:
```python
import requests

# make a bot
r = requests.post(url=f"https://recurse.rctogether.com/api/bots?app_id={ID}&app_secret={SEC}", json=your_json_bot_info)

# get info for all your bots - very useful for grabbing their ids!
r = requests.get(url=f"https://recurse.rctogether.com/api/bots?app_id={ID}&app_secret={SEC}")

# control your bot - like make it move, create things, etc
r = requests.patch(url=f"https://recurse.rctogether.com/api/bots/{bot_id}?app_id={ID}&app_secret={SEC}", json=your_new_bot_info)

# delete your bot :(
r = requests.delete(url=f"https://recurse.rctogether.com/api/bots/{bot_id}?app_id={ID}&app_secret={SEC}")
```
If your bot is not responsive (or not appearing at all), check requests with the attributes `r.status_code` and `r.text`. Successful requests will have status code 200. 401 means that your credentials were not accepted, and 422 means something required is missing or invalid - you should probably double-check your json.

It really is that simple! Don't be a n00b like me and waste time sifting through a new world message for your bot info. Seriously, I don't know why I wasted so much time doing that. Just use requests.get!