from pydantic import BaseModel


class TrainModelRequest(BaseModel):
    input_path: str
    target_column: str
    max_depth: int
    random_state: int
    chunk_size: int
    bucket_name: str
    excluded_columns: list
    patient_identifier: str
    label: str
    user_id: str
