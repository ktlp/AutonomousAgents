# AutonomousAgents

A minimal project that creates autonomous agents in pure Python!

## Overview

This project demonstrates the implementation of autonomous agents that communicate asynchronously, react to messages, and proactively generate new messages based on internal state or local time. The agents can represent humans, organizations, or entities in a specific domain and perform designated tasks autonomously.

### Requirements

    Python >= 3.7

### Installation

To install the project, clone the repository and install the dependencies:

```shell
git clone https://github.com/ktlp/AutonomousAgents.git
cd AutonomousAgents
pip install .
```

### Agent Features
#### Message Handling

- Continuous Consumption: Agents continuously consume messages from an InBox.
- Message Emission: Agents can emit messages to an OutBox.
- Handler Registration: Agents support the registration of message handlers to process specific message types.
- Behavior Registration: Agents support the registration of behaviors that generate messages based on internal state or scheduled times.


### Example Code
Here is an example to set up and run two agents, with the first one connected to the second:

```python
import asyncio
from autogents import Agent, MessageType1

async def main():
    # Create agent 1
    agent1 = Agent(name="Agent1", inbox=asyncio.Queue(), outbox=asyncio.Queue())

    # Create agent 2, its input connected to Agent1's output
    agent2 = Agent(name="Agent2", inbox=agent1.outbox, outbox=asyncio.Queue())

    # Tasks to run both agents
    tasks = [asyncio.create_task(agent1.run()),
             asyncio.create_task(agent2.run())]

    # Register a handler to Agent2 to print received messages
    async def print_messages(message: MessageType1):
        print(message)
    agent2.register_handler(print_messages)

    # Emit a message from Agent1
    await agent1.emit_message(MessageType1("Hello!"))

    # Allow some time for the message to be processed
    await asyncio.sleep(0.1)

    # Clean up tasks
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())

```

#### Important Note:
Behaviours are functions that receive an `Agent` object. To register successfully a behaviour
to an Agent, one must use the following function signature:
```python
from autogents import Agent
async def my_behaviour(agent: Agent):
    ...
```

In the same spirit, message handlers accept `BaseMessage` (or a class that inherits from it). The signature
in this case must follow the style:
```python
from autogents import BaseMessage
async def handler(message: BaseMessage):
    ...
```

### Testing
To run the tests, use the following command:
```shell
python -m unittest discover tests
```


### License
This project is licensed under the MIT License. See the LICENSE.md file for details.
