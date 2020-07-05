from threading import Thread
import traceback
import aiohttp
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
        loop.run_until_complete(self.do_polling())

    def _start_with_new_loop(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.do_polling())

    def start_async(self):
        self._thread = Thread(target=self._start_with_new_loop)
        self._thread.start()

    def get_polls(self):
        return []

    async def on_poll_data(self, *args, **kwargs):
        raise NotImplementedError()

    async def _poll(self, obj, func, delay):
        timeout = aiohttp.ClientTimeout(total=delay * 2)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            obj._session = session
            polls = 0
            polls_err = 0
            polls_no_err = 0
            while True:
                try:
                    args = await func()
                    await self.on_poll_data(*args, obj=obj, emit_empty=(polls == 0), emit_events=(polls_no_err > 0))
                    polls_no_err += 1
                except Exception as e:
                    self.on_event(
                        dict(
                            type="error",
                            name="polling",
                            desc=str(func),
                            traceback=repr(traceback.format_stack()) + " -> " + repr(e),
                            source=str(self),
                        )
                    )
                    polls_err += 1
                polls += 1
                if polls > 20 and polls_err / polls > 0.25:
                    self.on_event(dict(type="error", name="stop-polling", desc=str(func), source=str(self)))
                    break
                await asyncio.sleep(self.delay)

    async def do_polling(self):
        polls = await self.get_polls()
        await asyncio.gather(*[self._poll(o, f, d) for o, f, d in polls])
