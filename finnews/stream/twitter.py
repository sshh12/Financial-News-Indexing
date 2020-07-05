from finnews.articles import clean_html_text, extract_symbols
from finnews.config import config
from finnews.stream.abs import Stream
import tweepy


CREDS = config["creds"]["twitter"]
CFG = config["watch"]["twitter"]


class _Listener(tweepy.StreamListener):
    def on_status(self, status):
        print(status)

    def on_exception(self, err):
        print(err)

    def on_error(self, status_code):
        print(status_code)


class StreamTwitter(Stream):
    def __init__(self):
        self.auth = tweepy.OAuthHandler(CREDS["consumer_key"], CREDS["consumer_secret"])
        if "oauth_key" not in CREDS:
            redirect_url = self.auth.get_authorization_url()
            print(redirect_url)
            code = input("code > ")
            params = self.auth.get_access_token(code)
            print(params)
        self.auth.set_access_token(CREDS["oauth_key"], CREDS["oauth_secret"])
        self.api = tweepy.API(self.auth)
        self.name_to_symb = {}
        for sym, list_ in CFG.items():
            self.name_to_symb.update({name: sym for name in list_})

    def start(self):
        users = [self._name_to_id(name) for name in self.name_to_symb]
        while True:
            try:
                self._run(users)
            except Exception as e:
                self.on_event(dict(type="error", name="twitter", desc=str(e), source=str(self)))

    def _run(self, user_ids):
        listener = _Listener()
        listener.on_status = self._on_tweet
        stream = tweepy.Stream(auth=self.api.auth, listener=listener)
        stream.filter(follow=user_ids)

    def _name_to_id(self, name):
        return str(self.api.get_user(name).id)

    def _parse_tweet(self, status):
        text = None
        if hasattr(status, "retweeted_status"):
            try:
                text = status.retweeted_status.extended_tweet["full_text"]
            except AttributeError:
                text = status.retweeted_status.text
        else:
            try:
                text = status.extended_tweet["full_text"]
            except AttributeError:
                text = status.text
        return clean_html_text(text)

    def _on_tweet(self, tweet):
        text = self._parse_tweet(tweet)
        if len(text) == 0:
            return
        name = tweet.author.screen_name
        if name not in self.name_to_symb:
            return
        data = dict(source="twitter", type="tweet", text=text, author=name)
        symbs = extract_symbols(text)
        symb = self.name_to_symb.get(name)
        if symb is not None and symb != "_":
            symbs.add(symb)
        data["symbols"] = list(symbs)
        self.on_event(data)
