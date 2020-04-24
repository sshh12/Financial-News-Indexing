from stream.twitter import StreamTwitter


def on_event(evt):
    print('!!!!', evt)


def main():
    twitter = StreamTwitter()
    twitter.on_event = on_event
    twitter.start()


if __name__ == '__main__':
    main()