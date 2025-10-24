from fastapi import HTTPException

class BadRequestError(HTTPException):
    def __init__(self, index: str):
        super().__init__(status_code=400, detail=index)