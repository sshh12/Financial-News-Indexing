from finnews.watch import watch_all_forever


def on_event(evt):
    print(evt)


if __name__ == "__main__":
    watch_all_forever(on_event)
