import requests
import time


class Skier:
    def __init__(self, app_id, app_sec, name="Skier1", x=54, y=103, emoji="⛷️"):
        self.init_json = {
            "bot": {
                "name": name,
                "emoji": emoji,
                "x": x,
                "y": y,
                "direction": "down",
                "can_be_mentioned": False
            }
        }
        self.name = name
        self.id = None
        self.message = None
        self.pos = {
            "x": x,
            "y": xy
        }
        self.app_id = app_id
        self.app_sec = app_sec

    def make_message(self):
        from SkiRun import get_bot
        self.id = get_bot(self.name, 'id', self.app_id, self.app_sec)
        if self.id:
            self.message = {
                "bot_id": self.id,
                "message": "The powder is great today!"
            }
        else:
            print(f"Error: {self.name}.id is None. Run get_bot to set it!")

    def chairlift(self):
        ride = requests.post(url=f"https://recurse.rctogether.com/api/bots?app_id={self.app_id}&app_secret={self.app_sec}",
                             json=self.init_json)
        print(f"lift status: {ride}")
        runs = 0
        while runs < 5:
            self.ski_down()
            runs += 1
        self._wipeout()

    def ski_down(self):
        slope = self.pos['y']
        carve = self.pos['x']
        while slope < 109:
            wheee = {'bot': {'x': carve - 1, 'y': slope + 1}}
            r = requests.patch(
                url=f"https://recurse.rctogether.com/api/bots/{self.id}?app_id={self.app_id}&app_secret={self.app_sec}",
                json=wheee)
            slope += 1
            carve -= 1
            time.sleep(1)

    def _wipeout(self):
        d = requests.delete(
            url=f"https://recurse.rctogether.com/api/bots/{self.id}?app_id={self.app_id}&app_secret={self.app_sec}")
        print(f"delete skier status: {d.status_code}")
