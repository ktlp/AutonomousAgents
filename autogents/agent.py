from typing import Callable

import asyncio
import inspect

from autogents.messages import BaseMessage, MessageType1


class Agent:
    def __init__(self, name: str, inbox: asyncio.Queue, outbox: asyncio.Queue):
        self.name = name
        self.inbox = inbox
        self.outbox = outbox
        self.handlers = set()
        self.behaviours = {}

    async def run(self):
        tasks = [asyncio.create_task(self.consume_messages())]
        tasks.extend(list(self.behaviours.values()))
        await asyncio.gather(*tasks)

    async def run_behaviour(self, behaviour):
        while True:
            await behaviour(self)
            await asyncio.sleep(0)

    async def emit_message(self, message: BaseMessage):
        await self.outbox.put(message)

    async def consume_messages(self):
        while True:
            message = await self.inbox.get()
            self.inbox.task_done()

            for handler in self.handlers:
                await handler(message)

    def register_behaviour(self, behaviour: Callable):
        if not self._validate_behaviour(behaviour):
            raise ValueError("The behaviour is not valid.")
        task = asyncio.create_task(self.run_behaviour(behaviour))
        self.behaviours[behaviour] = task

    def register_handler(self, handler: Callable):
        if not self._validate_handler(handler):
            raise ValueError("The handler is not valid.")
        self.handlers.add(handler)

    def unregister_behaviour(self, behaviour: Callable):
        task = self.behaviours.pop(behaviour)
        if task:
            task.cancel()

    def unregister_handler(self, handler: Callable):
        self.handlers.discard(handler)

    @staticmethod
    def _validate_behaviour(behaviour: Callable) -> bool:
        signature = inspect.signature(behaviour)
        parameters = signature.parameters

        if len(parameters) != 1:
            return False

        parameter = list(parameters.values())[0]
        if parameter.annotation is parameter.empty:
            return False
        if parameter.annotation != Agent:
            return False
        return True

    @staticmethod
    def _validate_handler(handler: Callable) -> bool:
        signature = inspect.signature(handler)
        parameters = signature.parameters

        if len(parameters) != 1:
            return False
        parameter = list(parameters.values())[0]
        if parameter.annotation is parameter.empty:
            return False
        if not issubclass(parameter.annotation, BaseMessage):
            return False
        return True



