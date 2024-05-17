import asyncio
import os.path
import shutil
import tempfile
from fastapi import FastAPI, HTTPException
from packages.minio_file_handler import client
from packages.helpers.TrainModelRequestModel import TrainModelRequest
from packages.helpers.FileDownloadRequestModel import FileDownloadRequest
from packages.helpers.FileCleaningRequestModel import FileCleaningRequest
from packages.preprocessing.preprocess_data import preprocess_files
from packages.processing import random_forest

app = FastAPI()
minio_client = client.MinioClient()


@app.post("/download_files")
async def download_files(request: FileDownloadRequest):
    temporary_directory = tempfile.mkdtemp()

    try:
        await asyncio.get_event_loop().run_in_executor(
            None,
            minio_client.get_files_by_user_label,
            request.bucket_name, request.user_id, request.label, temporary_directory
        )

        return {"message": "Files retrieved successfully.", "file_path": temporary_directory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clean_files")
async def clean_files(request: FileCleaningRequest):
    try:
        if not os.path.exists(request.input_path):
            raise HTTPException(status_code=404, detail="Input path not found")

        output_path = tempfile.mkdtemp()

        preprocess_files(request.input_path,
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
    finally:
        shutil.rmtree(request.input_path)


@app.post("/train_model")
async def train_model(request: TrainModelRequest):
    temporary_directory = tempfile.mkdtemp()

    try:
        random_forest.run(request.input_path,
                          temporary_directory,
                          request.target_column,
                          request.max_depth,
                          request.random_state,
                          request.chunk_size,
                          request.excluded_columns)
        minio_client.upload_directory(request.bucket_name, request.user_id, request.label, temporary_directory)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(temporary_directory)
        shutil.rmtree(request.input_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
