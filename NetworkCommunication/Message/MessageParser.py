from Message.ByteMessage import ByteMessage


class MessageParser:
    def __init__(self, message_classes: [ByteMessage]):
        self.parsable_types = {item.CONTENT_TYPE: item for item in message_classes}

    def parse(self, header, content):
        return self.parsable_types[header[ByteMessage.HEADER_CONTENT_TYPE]]\
            .decode_message(content, header[ByteMessage.HEADER_CONTENT_ENCODING])
