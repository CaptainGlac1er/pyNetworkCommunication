from socketserver import StreamRequestHandler

from Message.MessageIO import MessageIO
from Server.ServerHandler import ServerHandler


class ServerClientConnection(StreamRequestHandler):
    def __init__(self, handler: ServerHandler, message_parser, request, client_address, server):
        self.message_reader = None
        self.handler = handler
        self.message_parser = message_parser
        StreamRequestHandler.__init__(self, request, client_address, server)

    def setup(self):
        StreamRequestHandler.setup(self)
        self.handler.add_connection(self.connection)
        self.message_reader = MessageIO(self.connection, self.message_parser)

    def handle(self):
        while True:
            print('listening for next message')
            self.handler.process_message(self.message_reader.read_next_message())


