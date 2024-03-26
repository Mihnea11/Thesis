import asyncio
import os.path
import tempfile
from fastapi import FastAPI, HTTPException
from packages.minio_file_handler import client
from packages.helpers.FileDownloadRequestModel import FileDownloadRequest
from packages.helpers.FileCleaningRequestModel import FileCleaningRequest


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

        # TO DO: CALL CLEANING ALGORITHM WITH NECESSARY PARAMETERS

        os.remove(request.input_path)

        return {"message": "Files cleaned successfully", "cleaned_files_path": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
