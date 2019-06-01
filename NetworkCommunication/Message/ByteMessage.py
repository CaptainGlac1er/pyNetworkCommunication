from Message.Message import Message


class ByteMessage(Message):
    CONTENT_TYPE = 'bytes'

    def __init__(self,
                 content,
                 custom_headers=None,
                 content_type=CONTENT_TYPE,
                 content_encoding=Message.DEFAULT_ENCODING):
        super().__init__(content, custom_headers, content_type, content_encoding)

    def encode_content_as_bytes(self):
        return self.content

    def decode_content(self, content, content_encoding):
        return content

    @staticmethod
    def decode_message(content, headers):
        return ByteMessage(content, custom_headers=headers, content_encoding=headers[Message.HEADER_CONTENT_ENCODING])
