import time
import uuid
from typing import Optional

from pydantic import BaseModel, validator

from service_sign import get_req_sign
from settings import APP_ID


class ReqParams(BaseModel):
    app_id: int = APP_ID
    time_stamp: int = None
    nonce_str: str = None
    format: int = 2
    callback_url: str
    speech: str

    @validator("time_stamp", always=True)
    def default_timestamp(cls, v):
        return v or int(time.time())

    @validator("nonce_str", always=True)
    def default_nonce_str(cls, v):
        return v or str(uuid.uuid4())[:32]

    def req_params(self):
        assert len(self.dict(exclude_none=True)) == 6, "parmas not set"
        sign = get_req_sign(self.dict())
        return {**self.dict(), **{"sign": sign}}


class Tsk(BaseModel):
    task_id: str


class ResData(BaseModel):
    ret: int
    msg: str = None
    data: Optional[Tsk] = None


class ResultModel(BaseModel):
    ret: int = 1
    message: str = None
