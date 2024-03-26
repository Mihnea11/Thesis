from pydantic import BaseModel


class FileCleaningRequest(BaseModel):
    input_path: str
    patient_identifier: str
    excluded_columns: list[str]
    encoding_method: str
    row_threshold: int
    column_threshold: int
