from pydantic import BaseModel


class HTTPErrorDetail(BaseModel):
    category: str
    code: int
    msg: str


class HTTPError(BaseModel):
    detail: HTTPErrorDetail

    class Config:
        schema_extra = {"example": {"detail": "HTTPException raised."}}
