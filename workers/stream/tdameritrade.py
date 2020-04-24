from config import config
from . import Stream
from urllib.parse import urlencode
import requests
import websocket
import _thread as thread
import pendulum
import json
import time


CREDS = config['creds']['tda']


class TDA:

    def __init__(self, consumer_key, redirect_uri='http://localhost', access_token=None):
        self.consumer_key = consumer_key
        self.redirect_uri = redirect_uri
        self.access_token = access_token

    def _do_api(self, path, params=None, method='GET'):
        kwargs = {}
        kwargs['headers'] = {'Authorization': 'Bearer ' + self.access_token}
        if params is not None:
            kwargs['params'] = params
        resp = requests.get('https://api.tdameritrade.com/v1/' + path, **kwargs)
        return resp.json()

    def do_auth(self):
        print('https://auth.tdameritrade.com/auth?' + 
            'response_type=code&redirect_uri={}&client_id={}@AMER.OAUTHAP'.format(self.redirect_uri, self.consumer_key))
        code = input('code > ')
        resp = requests.post('https://api.tdameritrade.com/v1/oauth2/token', data=dict(
            grant_type='authorization_code', 
            access_type='offline', 
            client_id=self.consumer_key + '@AMER.OAUTHAP', 
            redirect_uri=self.redirect_uri, 
            code=code
        )).json()
        print('ACCESS', resp['access_token'])
        print('REFRESH', resp['refresh_token'])

    def get_user_principles(self):
        return self._do_api('userprincipals', params=dict(fields='streamerSubscriptionKeys,streamerConnectionInfo'))

    def _format_stream_req(self, service, command, params, account, source, id_=None, _id_cnt=[0]):
        if id_ is None:
            _id_cnt[0] += 1
            id_ = _id_cnt[0]
        return {
            'service': service.upper(),
            'command': command.upper(),
            'requestid': str(id_),
            'account': account,
            'source': source,
            'parameters': params
        }

    def stream(self):
        principles = self.get_user_principles()
        stream = TDAStream(principles)
        return stream


class TDAStream:

    def __init__(self, principles):
        self.principles = principles
        self.ws_uri = 'wss://' + principles['streamerInfo']['streamerSocketUrl'] + '/ws'
        self.token_ts = int(pendulum.parse(principles['streamerInfo']['tokenTimestamp']).float_timestamp * 1000)
        self.acc_id = principles['accounts'][0]['accountId']
        self.app_id = principles['streamerInfo']['appId']
        self.req_id_cnt = 0
        self.ws = None

    def cmd(self, service, command, params, id_=None):
        if id_ is None:
            self.req_id_cnt += 1
            id_ = self.req_id_cnt
        for key, val in params.items():
            if type(val) == list:
                params[key] = ','.join([str(v) for v in val])
        reqs = {
            'requests': [
                {
                    'service': service.upper(),
                    'command': command.upper(),
                    'requestid': str(id_),
                    'account': self.acc_id,
                    'source': self.app_id,
                    'parameters': params
                }
            ]
        }
        self.ws.send(json.dumps(reqs))

    def start(self):
        creds = {
            'userid': self.acc_id,
            'token': self.principles['streamerInfo']['token'],
            'company': self.principles['accounts'][0]['company'],
            'segment': self.principles['accounts'][0]['segment'],
            'cddomain': self.principles['accounts'][0]['accountCdDomainId'],
            'usergroup': self.principles['streamerInfo']['userGroup'],
            'accesslevel': self.principles['streamerInfo']['accessLevel'],
            'authorized': 'Y',
            'timestamp': self.token_ts,
            'appid': self.app_id,
            'acl': self.principles['streamerInfo']['acl']
        }
        login_params = {
            'credential': urlencode(creds),
            'token': self.principles['streamerInfo']['token'],
            'version': '1.0'
        }
        logged_in = [False]
        def on_login():
            logged_in[0] = True
            print('LOGIN COMPLETE')
        def on_message(ws, msg):
            data = json.loads(msg)
            for resp in data['response']:
                if resp['requestid'] == 'login':
                    on_login()
                else:
                    print(resp)
        def on_error(ws, error):
            print(error)
        def on_close(ws):
            print("### closed ###")
        def on_open(ws):
            self.ws = ws
            self.cmd('admin', 'login', login_params, id_='login')
        ws = websocket.WebSocketApp(self.ws_uri, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
        thread.start_new_thread(ws.run_forever, ())
        while not logged_in[0]:
            time.sleep(0.25)


tda = TDA(CREDS['consumer_key'], access_token=CREDS['access_token'])
strm = tda.stream()
strm.start()
import time
time.sleep(1)
strm.cmd('news_headline', 'subs', {'keys': ['GOOG', 'MESO', 'AAPL', 'TSLA', 'FB'], 'fields': [0, 1, 2, 3, 4]})
while True:
    time.sleep(1)

class StreamTDA(Stream):

    def __init__(self):
        pass

    def start(self):
        pass