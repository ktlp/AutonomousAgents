import unittest
from autogents import Agent, MessageType1
import asyncio


class TestAgent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.queue1 = asyncio.Queue()
        self.queue2 = asyncio.Queue()
        self.agent = Agent(name="Agent1", inbox=self.queue1, outbox=self.queue2)

    async def asyncTearDown(self):
        for behaviour_task in self.agent.behaviours.values():
            behaviour_task.cancel()

    async def test_emit_message(self):
        message = MessageType1(content="test")
        await self.agent.emit_message(message)

        message_received = await self.queue2.get()
        self.assertIsInstance(message_received, MessageType1)
        self.assertEqual(message_received.content, "test")

    async def test_register_and_run_behaviour(self):
        counter = 0

        async def behaviour(agent: Agent):
            nonlocal counter
            await asyncio.sleep(0.1)
            counter += 1

        self.agent.register_behaviour(behaviour)
        task = asyncio.create_task(self.agent.run())

        await asyncio.sleep(0.5)

        self.assertGreater(counter, 0)

        self.agent.unregister_behaviour(behaviour)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    async def test_register_and_run_handler(self):
        counter = 0

        async def handler(message: MessageType1):
            nonlocal counter
            counter += 1

        self.agent.register_handler(handler)
        task = asyncio.create_task(self.agent.run())
        await asyncio.sleep(0.1)
        await self.queue1.put(MessageType1(content="test"))
        await asyncio.sleep(0.1)

        self.assertEqual(counter, 1)

        self.agent.unregister_handler(handler)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    async def test_deregister_handler(self):
        from copy import deepcopy

        counter = 0

        async def behaviour(agent: Agent):
            nonlocal counter
            await asyncio.sleep(0.01)
            counter += 1

        self.agent.register_behaviour(behaviour)
        task = asyncio.create_task(self.agent.run())

        await asyncio.sleep(0.1)
        initial_calls = deepcopy(counter)
        self.agent.unregister_behaviour(behaviour)
        await asyncio.sleep(0.1)
        self.assertEqual(initial_calls, counter)

        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    async def test_unregister_handler(self):
        counter = 0

        async def test_handler(message: MessageType1):
            nonlocal counter
            counter += 1

        self.agent.register_handler(test_handler)

        message = MessageType1(content="test1")
        message2 = MessageType1(content="test2")
        await self.agent.inbox.put(message)
        task = asyncio.create_task(self.agent.consume_messages())
        await asyncio.sleep(0.1)
        self.agent.unregister_handler(test_handler)
        await self.agent.inbox.put(message2)
        await asyncio.sleep(0.1)

        self.assertEqual(counter, 1)

        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    async def test_validate_behaviour(self):
        async def valid_behaviour(agent: Agent):
            pass

        async def invalid_behaviour():
            pass

        with self.assertRaises(ValueError) as _:
            self.agent.register_behaviour(invalid_behaviour)

        self.agent.register_behaviour(valid_behaviour)
        self.assertEqual(len(self.agent.behaviours), 1)

        self.agent.unregister_behaviour(valid_behaviour)

    async def test_validate_handler(self):
        async def valid_handler(message: MessageType1):
            pass

        async def invalid_handler():
            pass

        with self.assertRaises(ValueError) as _:
            self.agent.register_handler(invalid_handler)

        self.agent.register_handler(valid_handler)
        self.assertEqual(len(self.agent.handlers), 1)

        self.agent.unregister_handler(valid_handler)


if __name__ == "__main__":
    unittest.main()
