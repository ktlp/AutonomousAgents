from autogents import Agent, MessageType1, BaseMessage

import asyncio
import random


async def random_messages_behaviour(agent: Agent):
    alphabet = [
        "hello",
        "sun",
        "world",
        "space",
        "moon",
        "crypto",
        "sky",
        "ocean",
        "universe",
        "human",
    ]
    await asyncio.sleep(2)
    content = " ".join(random.choices(alphabet, k=2))
    await agent.emit_message(MessageType1(content=content))
    return


async def filtering_handler(message: BaseMessage):
    if "hello" in message.content:
        print(message)


async def main(runtime: int):
    inbox_agent1 = asyncio.Queue()
    inbox_agent2 = asyncio.Queue()
    agent1 = Agent(name="Agent1", inbox=inbox_agent1, outbox=inbox_agent2)
    agent2 = Agent(name="Agent2", inbox=inbox_agent2, outbox=inbox_agent1)
    agent1.register_handler(filtering_handler)
    agent2.register_handler(filtering_handler)
    agent1.register_behaviour(random_messages_behaviour)
    agent2.register_behaviour(random_messages_behaviour)
    tasks = [asyncio.create_task(agent1.run()), asyncio.create_task(agent2.run())]

    await asyncio.sleep(runtime)

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main(runtime=20))
