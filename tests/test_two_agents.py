import unittest
import asyncio
from autogents.messages import BaseMessage, MessageType1
from autogents import Agent


class IntegrationTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.queue1 = asyncio.Queue()
        self.queue2 = asyncio.Queue()
        self.agent1 = Agent(name="Agent1", inbox=self.queue1, outbox=self.queue2)
        self.agent2 = Agent(name="Agent2", inbox=self.queue2, outbox=self.queue1)

        self.agent1.register_handler(self.filtering_handler_Agent1)
        self.agent2.register_handler(self.filtering_handler_Agent2)
        self.agent1_received_messages = []
        self.agent2_received_messages = []

    async def filtering_handler_Agent1(self, message: BaseMessage):
        self.agent1_received_messages.append(message)

    async def filtering_handler_Agent2(self, message: BaseMessage):
        self.agent2_received_messages.append(message)

    async def test_agents_emission(self):
        """
        Test the emission and reception of messages between two agents connected in a loop.
        """
        tasks = [
            asyncio.create_task(self.agent1.run()),
            asyncio.create_task(self.agent2.run()),
        ]

        await self.agent1.emit_message(MessageType1("hello from Agent1!"))
        await self.agent2.emit_message(MessageType1("hello from Agent2!"))
        await asyncio.sleep(0.1)

        self.assertEqual(len(self.agent1_received_messages), 1)
        self.assertEqual(len(self.agent1_received_messages), 1)
        self.assertEqual(self.agent2_received_messages[0].content, "hello from Agent1!")
        self.assertEqual(self.agent1_received_messages[0].content, "hello from Agent2!")

        await self.agent1.emit_message(MessageType1("hello, again from Agent1!"))
        await asyncio.sleep(0.1)

        self.assertEqual(len(self.agent1_received_messages), 1)
        self.assertEqual(len(self.agent2_received_messages), 2)
        self.assertEqual(
            self.agent2_received_messages[-1].content, "hello, again from Agent1!"
        )

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

        self.agent2_received_messages = []
        self.agent1_received_messages = []

    async def test_agents_with_behaviour(self):
        """
        Test the scenario where an agent that emits messages at a regular interval (via behavior), and the other one
        is listening (via handler).
        """

        async def behaviour(agent: Agent):
            for _ in range(5):
                await agent.emit_message(message=MessageType1("This is your alarm."))
                await asyncio.sleep(0.2)

        self.agent1.register_behaviour(behaviour)

        tasks = [
            asyncio.create_task(self.agent1.run()),
            asyncio.create_task(self.agent2.run()),
        ]

        await asyncio.sleep(1.5)

        self.assertGreater(len(self.agent2_received_messages), 5)
        for item in self.agent2_received_messages:
            self.assertEqual(item.content, "This is your alarm.")

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    unittest.main()
