class File:
    """A simple class that represents an in memory file, useful for manipulation on the client side"""
    def __init__(self, fileName, content, key):
        self.fileName = fileName
        self.content = content
        self.key = key
    def write(self, content, token):
        response = sendWrite(self.fileName, content, token)
        if response != -1:
            self.content = content
            return 0
        return -1
class WriteError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

