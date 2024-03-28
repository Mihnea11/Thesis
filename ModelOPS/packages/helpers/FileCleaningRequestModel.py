from pydantic import BaseModel


class FileCleaningRequest(BaseModel):
    input_path: str
    patient_identifier: str
    encoding_method: str
    scale_method: str
    row_threshold: float
    column_threshold: float
    excluded_columns: list[str]
