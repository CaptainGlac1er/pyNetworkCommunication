import json
import struct

from Message.ByteMessage import ByteMessage
from Message.MessageParser import MessageParser


class MessageIO:
    def __init__(self, file, message_parsers: MessageParser):
        self.file = file
        self.message_parser = message_parsers

    def read_next_message(self) -> ByteMessage:
        header_length = struct.unpack('>H', self.file.read(2))[0]
        header = json.loads(self.file.read(header_length).decode(ByteMessage.DEFAULT_ENCODING))
        content_length = header[ByteMessage.HEADER_CONTENT_LENGTH]
        content = self.file.read(content_length)
        return self.message_parser.parse(header, content)
