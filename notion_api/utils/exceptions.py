class APIRequestError(Exception):
    """APIリクエストに失敗した場合の例外"""
    pass

class APIClientNotFountError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
