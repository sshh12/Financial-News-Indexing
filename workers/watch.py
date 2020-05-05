from stream.twitter import StreamTwitter
from stream.tdameritrade import StreamTDA
from stream.prs import StreamPRs
from stream.news import StreamNews
from notify.slack import slack_evt

import nest_asyncio; nest_asyncio.apply()


def on_event(evt):
    print(evt)


def main():
    
    strm_twitter = StreamTwitter()
    strm_twitter.on_event = on_event
    strm_twitter.start_async()

    strm_tda = StreamTDA()
    strm_tda.on_event = on_event
    strm_tda.start_async()

    strm_prs = StreamPRs()
    strm_prs.on_event = on_event
    strm_prs.start_async()

    strm_news = StreamNews()
    strm_news.on_event = on_event
    strm_news.start()


if __name__ == '__main__':
    main()