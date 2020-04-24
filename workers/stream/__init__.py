from threading import Thread


class Stream:

    def __init__(self):
        pass

    def start(self):
        pass

    def start_async(self):
        self._thread = Thread(target=self.start)
        self._thread.start()

    def on_event(self, evt):
        pass