from fastapi import HTTPException

class ForbiddenError(HTTPException):
    def __init__(self, index: str):
        super().__init__(status_code=401, detail=f'Acesso Negado!: {index}')