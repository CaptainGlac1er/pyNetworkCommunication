from Message.MessageParser import MessageParser
from Server.ServerClientConnection import ServerClientConnection


class ServerClientConnectionFactory:
    def __init__(self, message_parsers, router=None):
        self.router = router
        self.message_parsers = MessageParser(message_parsers)

    def create_with_router(self, request, client_address, server):
        return ServerClientConnection(self.router, self.message_parsers, request, client_address, server)
