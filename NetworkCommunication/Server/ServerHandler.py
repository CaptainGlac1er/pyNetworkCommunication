import threading
import logging
from uuid import UUID

from Message.Message import Message
from Server import ServerClientConnection


class ServerHandler:
    def __init__(self):
        self.connections: {UUID: ServerClientConnection} = {}
        self.connections_lock: threading.Lock = threading.Lock()

    def add_connection(self, connection: ServerClientConnection):
        with self.connections_lock:
            logging.info(f'{"Server: ":>10s} client {connection.get_uuid()} connected')
            self.connections[connection.get_uuid()] = connection
            logging.debug(f'{"Server: ":>10s} has now {len(self.connections)} connections')

    def remove_connection(self, connection: ServerClientConnection):
        with self.connections_lock:
            logging.info(f'{"Server: ":>10s} client {connection.get_uuid()} disconnected')
            connection.close_connection()
            if connection.get_uuid() in self.connections:
                del self.connections[connection.get_uuid()]
            print(self.connections)
            logging.debug(f'{"Server: ":>10s} has now {len(self.connections)} connections')

    def get_connections(self):
        with self.connections_lock:
            return list(self.connections.items())

    def process_message(self, uuid, message: Message):
        pass
