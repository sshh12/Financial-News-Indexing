from finnews.stream.twitter import StreamTwitter
from finnews.stream.tdameritrade import StreamTDA
from finnews.stream.prs import StreamPRs
from finnews.stream.news import StreamNews
from finnews.stream.stats import StreamStats
from finnews.stream.guru import StreamGuru

STREAMS = {"tda": StreamTDA, "twitter": StreamTwitter, "prs": StreamPRs, "stats": StreamStats, "news": StreamNews, "guru": StreamGuru}


def run_streams(streams, on_event):
    strms = []
    for Stream in streams:
        strm = Stream()
        strm.on_event = on_event
        strms.append(strm)
    for i, stream in enumerate(strms):
        if i == len(strms) - 1:
            stream.start()
        else:
            stream.start_async()
