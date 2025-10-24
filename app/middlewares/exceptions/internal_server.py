from fastapi import HTTPException

class InternalServerError(HTTPException):
    def __init__(self, index: str):
        super().__init__(status_code=500, detail=index)