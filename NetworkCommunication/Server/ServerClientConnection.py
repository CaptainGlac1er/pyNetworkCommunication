import logging
import socket
import uuid
from socketserver import StreamRequestHandler
from typing import Optional

from Message import Message, MessageIO
from Server import ServerHandler


class ServerClientConnection(StreamRequestHandler):
    def __init__(self, handler: ServerHandler, message_parser, request, client_address, server):
        self.message_reader: Optional[MessageIO] = None
        self.uuid = uuid.uuid4()
        self.handler = handler
        self.message_parser = message_parser
        StreamRequestHandler.__init__(self, request, client_address, server)

    def setup(self):
        StreamRequestHandler.setup(self)
        self.handler.add_connection(self)
        self.message_reader = MessageIO(self.connection)

    def handle(self):
        while True:
            message_received = self.message_reader.read_next_message(self.message_parser)
            if message_received:
                logging.debug((f'{"Server: ":>10s} received message {message_received.get_hash()}'
                               f' from {self.uuid}'))
                self.handler.process_message(self.uuid, message_received)
            else:
                self.handler.remove_connection(self)
                break

    def close_connection(self):
        if self.connection is not None:
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()

    def send_message(self, message: Message):
        logging.debug((f'{"Server: ":>10s} sending message {message.get_hash()}'
                       f' to {self.uuid}'))
        self.message_reader.send_message(message)

    def get_uuid(self):
        return self.uuid
