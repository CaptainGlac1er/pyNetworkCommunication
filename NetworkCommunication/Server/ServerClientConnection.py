from socketserver import StreamRequestHandler

from Message.MessageIO import MessageIO


class ServerClientConnection(StreamRequestHandler):
    def __init__(self, callback, message_parser, request, client_address, server):
        self.message_reader = None
        self.callback = callback
        self.message_parser = message_parser
        StreamRequestHandler.__init__(self, request, client_address, server)
        print(self.connection)
        print('Made Connection')

    def setup(self):
        StreamRequestHandler.setup(self)
        self.message_reader = MessageIO(self.connection, self.message_parser)

    def handle(self):
        while True:
            print('listening for next message')
            current_message = self.message_reader.read_next_message()
            print(current_message.get_content())


