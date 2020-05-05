from threading import Thread
import asyncio


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


class StreamPoll(Stream):

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._start_polling())

    def _start_with_new_loop(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._start_polling())

    def start_async(self):
        self._thread = Thread(target=self._start_with_new_loop)
        self._thread.start()

    async def _start_polling(self):
        i = 0
        while True:
            try:
                await self._poll(print_empty=(i == 0), emit_events=(i > 0))
            except Exception as e:
                print('Poll error', e)
            await asyncio.sleep(self.delay)
            i += 1