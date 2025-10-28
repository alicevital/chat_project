from fastapi import HTTPException

class NotFoundError(HTTPException):
    def __init__(self, index: str):
        super().__init__(status_code=404, detail=f"{index} não encontrado")