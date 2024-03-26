from pydantic import BaseModel


class FileDownloadRequest(BaseModel):
    bucket_name: str
    user_id: str
    label: str
