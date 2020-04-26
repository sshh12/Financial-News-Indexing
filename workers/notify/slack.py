from slack import WebClient
from config import config


slack_client = WebClient(token=config['creds']['slack']['token'])


def slack_evt(evt):
    if 'symbols' in evt and 'title' in evt and 'url' in evt:
        msg = '*{}* {} {}'.format(evt['symbols'], evt['title'], evt['url'])
    else:
        msg = str(evt)
    slack_client.chat_postMessage(
        channel=config['creds']['slack']['channel'],
        text=msg)