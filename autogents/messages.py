class BaseMessage:
    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return self.content

    def __repr__(self):
        return self.content


class MessageType1(BaseMessage):
    def __init__(self, content: str):
        super().__init__(content)


class MessageType2(BaseMessage):
    def __init__(self, content: str):
        super().__init__(content)
