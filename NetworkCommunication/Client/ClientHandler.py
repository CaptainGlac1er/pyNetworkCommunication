import logging
from typing import Optional

from Client import Client
from Message import Message


class ClientHandler:
    def __init__(self):
        self.connection: Optional[Client] = None

    def set_connection(self, connection: Client):
        self.connection = connection

    def connection_closed(self, connection: Client, died: bool):
        if died and connection.is_connection_open():
            logging.info('connection died')
            connection.reconnect()
        else:
            logging.info('connection closed')
            connection.close()

    def process_message(self, message: Message):
        pass
