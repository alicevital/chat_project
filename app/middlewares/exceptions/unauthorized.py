from fastapi import HTTPException

class UnauthorizedError(HTTPException):
    def __init__(self, index: str):
        super().__init__(status_code=401, detail=index)