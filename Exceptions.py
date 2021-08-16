class ResponseTimeout(Exception):
    def __init__(self):
        self.message = "URL을 받아올 수 없습니다."

    def __str__(self):
        return str(self.message)