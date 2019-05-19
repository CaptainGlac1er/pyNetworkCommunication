import uuid
from socketserver import StreamRequestHandler
from typing import Optional

from Message.Message import Message
from Message.MessageIO import MessageIO
from Server.ServerHandler import ServerHandler


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
            print(f'{"Server: ":>10s} is listening for next message')
            self.handler.process_message(self.uuid, self.message_reader.read_next_message(self.message_parser))

    def send_message(self, message: Message):
        self.message_reader.send_message(message)

    def get_uuid(self):
        return self.uuid
