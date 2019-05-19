from uuid import UUID

from Message.Message import Message
from Server import ServerClientConnection


class ServerHandler:
    def __init__(self):
        self.connections: {UUID: ServerClientConnection} = {}

    def add_connection(self, connection: ServerClientConnection):
        pass

    def process_message(self, uuid, message: Message):
        pass

    def send_message(self, message: Message):
        pass