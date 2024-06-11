import asyncio
import os.path
import shutil
import tempfile
from fastapi import FastAPI, HTTPException
from packages.processing import random_forest
from packages.minio_file_handler import client
from packages.statistical_analysis import statistical_analysis
from packages.preprocessing.preprocess_data import preprocess_files
from packages.helpers.TrainModelRequestModel import TrainModelRequest
from packages.helpers.FileDownloadRequestModel import FileDownloadRequest
from packages.helpers.FileCleaningRequestModel import FileCleaningRequest

app = FastAPI()
minio_client = client.MinioClient()


@app.post("/download_files")
async def download_files(request: FileDownloadRequest):
    temporary_directory = tempfile.mkdtemp()

    try:
        output_path = os.path.join(temporary_directory, 'data')

        await asyncio.get_event_loop().run_in_executor(
            None,
            minio_client.get_files_by_user_label,
            request.bucket_name, request.user_id, request.label, output_path
        )

        return {"message": "Files retrieved successfully.", "file_path": temporary_directory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clean_files")
async def clean_files(request: FileCleaningRequest):
    try:
        if not os.path.exists(request.input_path):
            raise HTTPException(status_code=404, detail="Input path not found")

        input_path = os.path.join(request.input_path, 'data')
        output_path = os.path.join(request.input_path, 'cleaned')

        preprocess_files(input_path,
                         output_path,
                         request.patient_identifier,
                         request.encoding_method,
                         request.scale_method,
                         request.row_threshold,
                         request.column_threshold,
                         request.excluded_columns)
        return {"message": "Files cleaned successfully", "cleaned_files_path": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train_model")
async def train_model(request: TrainModelRequest):
    temporary_directory = tempfile.mkdtemp()

    try:
        if request.excluded_columns is None:
            request.excluded_columns = []

        if request.patient_identifier not in request.excluded_columns:
            request.excluded_columns.append(request.patient_identifier)

        default_directory = os.path.join(request.input_path, 'data')
        cleaned_directory = os.path.join(request.input_path, 'cleaned')

        if os.path.exists(cleaned_directory):
            input_path = cleaned_directory
        else:
            input_path = default_directory

        random_forest.run(input_path,
                          temporary_directory,
                          request.target_column,
                          request.max_depth,
                          request.random_state,
                          request.chunk_size,
                          request.excluded_columns)

        statistical_analysis.analyze(default_directory,
                                     temporary_directory,
                                     request.target_column,
                                     request.patient_identifier)
        minio_client.upload_directory(request.bucket_name, request.user_id, request.label, temporary_directory)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(request.input_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
