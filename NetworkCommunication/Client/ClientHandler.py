from typing import Optional

from Client import Client
from Message import Message


class ClientHandler:
    def __init__(self):
        self.connection: Optional[Client] = None

    def set_connection(self, connection: Client):
        self.connection = connection

    def connection_closed(self, connection: Client, died: bool):
        pass

    def process_message(self, message: Message):
        pass
