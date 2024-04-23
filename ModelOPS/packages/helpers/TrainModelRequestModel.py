from pydantic import BaseModel


class TrainModelRequest(BaseModel):
    something: str
