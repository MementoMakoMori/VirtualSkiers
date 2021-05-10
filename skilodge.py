import re
from skier import Skier
import requests
import time


class SkiLodge:

    def __init__(self, app_id, app_sec, name="RC Lodge", x=45, y=109, direction="left", emoji="🏠"):
        self.app_id = app_id
        self.app_sec = app_sec
        self.id = None
        self.name = name
        self.skiers = {}
        self.notes = None
        self.messages = None
        self.note_id = None
        self.status = None
        self.init_json = {
            "bot": {
                "name": name,
                "emoji": emoji,
                "x": x,
                "y": y,
                "direction": direction,
                "can_be_mentioned": True,
            }
        }

    def new_lodge(self):
        build = requests.post(
            url=f"https://recurse.rctogether.com/api/bots?app_id={self.app_id}&app_secret={self.app_sec}",
            json=self.init_json)
        if build.status_code != 200:
            print("""
                Error: lodge construction failed
                Code: {}
                Text: {}
                """.format(build.status_code, build.text))
        else:
            from SkiRun import get_bot
            self.id = get_bot(self.name, 'id', app_id=self.app_id, app_sec=self.app_sec)
            self.status = 'open'
            self.make_notes()
            self.new_note()
            self.set_note('open')

    def new_note(self):
        self.make_notes()
        sign = requests.post(url=f"https://recurse.rctogether.com/api/notes?app_id={self.app_id}&app_secret={self.app_sec}",
                             json=self.notes['open'])
        # print(sign.status_code)
        # print(sign.text)
        # print(f"Lodge sign: {sign.status_code}")

    def make_notes(self):
        self.notes = {
            "open": {
                "bot_id": self.id,
                "note": {
                    "note_text": "You can ask @**RC Lodge** (politely) for a lift ticket.\
                                PM @**Rebecca Holley on Zulip if it isn't working."
                }
            },
            "close": {
                "bot_id": self.id,
                "note": {
                    "note_text": "The lodge is currently closed. You can ask @**Rebecca Holley** to run this bot. :)"
                }
            }
        }
        self.messages = {
            "no": {
                "bot_id": self.id,
                "text": "What kind of manners is that? These tickets are free, you know!"
            },
            "yes": {
                "bot_id": self.id,
                "text": "Enjoy the slopes!"
            },
            "what": {
                "bot_id": self.id,
                "text": "There's a line forming - do you want a ticket or not?"
            }
        }
        # print("notes + messages created.")

    def set_note(self, tag: str):
        post = requests.patch(
            url=f"https://recurse.rctogether.com/api/notes/{self.note_id}?app_id={self.app_id}&app_secret={self.app_sec}",
            json=self.notes[tag])
        # print(f"Lodge sign: {post.status_code}")

    def ask_lodge(self, text):
        if self._summertime(text):
            self._close_lodge()
        if self._bye(text):
            self._close_lodge()
            dn = requests.delete(
                url=f"https://recurse.rctogether.com/api/notes/{self.note_id}?bot_id={self.id}&app_id={self.app_id}&app_secret={self.app_sec}")
            print(dn.status_code)
            dl = requests.delete(
                url=f"https://recurse.rctogether.com/api/bots/{self.id}?app_id={self.app_id}&app_secret={self.app_sec}")
            return print(dl.status_code)
        nice = self._ticket_please(text)
        if nice == 2:
            self._sell_ticket()
        elif nice == 1:
            message = requests.post(
                url=f"https://recurse.rctogether.com/api/messages?app_id={self.app_id}&app_secret={self.app_sec}",
                json=self.messages['no'])
            # print(f"message no: {message.status_code}")
        else:
            message = requests.post(
                url=f"https://recurse.rctogether.com/api/messages?&app_id={self.app_id}&app_secret={self.app_sec}",
                json=self.messages['what'])
            # print(f"message what: {message.status_code}")

    def _sell_ticket(self):
        message = requests.post(
            url=f"https://recurse.rctogether.com/api/messages?app_id={self.app_id}&app_secret={self.app_sec}",
            json=self.messages['yes'])
        # print(f"message yes: {message.status_code}")
        self.skiers['Skier1'] = Skier(app_id=self.app_id, app_sec=self.app_sec, name="Skier1")
        time.sleep(2)
        self.skiers['Skier1'].chairlift()

    def _close_lodge(self):
        from SkiRun import get_bot
        for skier in self.skiers:
            if get_bot(self.skiers[skier].name, app_id=self.app_id, app_sec=self.app_sec):
                self.skiers[skier]._wipeout()
        self.set_note('close')
        self.status = 'closed'

    _ticket = re.compile("ticket", flags=re.IGNORECASE)
    _please = re.compile("please", flags=re.IGNORECASE)
    _summer = re.compile("summer", flags=re.IGNORECASE)
    _goodbye = re.compile("goodbye", flags=re.IGNORECASE)

    def _ticket_please(self, text: str) -> int:
        ask = []
        for i in [self._ticket, self._please]:
            ask.append(int(bool(i.search(text))))
        return sum(ask)

    def _summertime(self, text: str) -> bool:
        return bool(self._summer.search(text))

    def _bye(self, text: str) -> bool:
        return bool(self._goodbye.search(text))
