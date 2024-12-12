from pydantic import BaseModel


class PingResponse(BaseModel):
    message: str


class DBResponse(BaseModel):
    status: str


class ExcResponse(BaseModel):
    message: str
