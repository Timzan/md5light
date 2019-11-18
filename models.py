from pydantic import BaseModel, UrlStr, EmailStr


class ChecksumIn(BaseModel):
    url: UrlStr
    email: EmailStr = None


class Checksum(ChecksumIn):
    id: int
    checksum: str = None

    class Config:
        orm_mode = True


class StatusResponse(BaseModel):
    status_id: str



