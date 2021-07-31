import datetime
from io import SEEK_CUR

class receipt:
    """
        Receipt data class
    """

    def __init__(
        self, 
        timestamp: datetime.datetime,
        date: datetime.datetime, 
        cause: str, 
        purpose: str,
        user_id: int, 
        username: str,
        js_name: str, 
        first_name: str,
        last_name: str,
        total: float,
        picture: str,
    ):
        self.timestamp = timestamp
        self.date = date
        self.cause = cause
        self.purpose = purpose
        self.user_id = user_id
        self.username = username
        self.js_name = js_name
        self.first_name = first_name
        self.last_name = last_name
        self.total = total
        self.picture = picture
