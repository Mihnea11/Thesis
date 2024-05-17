import os
from minio import Minio
from .config import MINIO_CONFIG


class MinioClient:
    def __init__(self):
        self.client = Minio(**MINIO_CONFIG)

    def get_files_by_user_label(self, bucket_name: str, user_id: str, label: str, local_storage_path: str) -> None:
        """
        Retrieve all files for a given user ID and label, and store them locally.

        :param bucket_name: Name of the Minio bucket.
        :param user_id: User ID as part of the object path.
        :param label: Label as part of the object path.
        :param local_storage_path: Base local path to store the retrieved files.
        """

        prefix = f"{user_id}/{label}/"
        objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)

        for obj in objects:
            local_path = os.path.join(local_storage_path, obj.object_name.replace(prefix, ""))
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            self.client.fget_object(bucket_name, obj.object_name, local_path)
            print(f"Downloaded {obj.object_name} to {local_path}")

    def upload_directory(self, bucket_name: str, user_id: str, label: str, directory_path: str) -> None:
        """
        Upload all files in a directory to a Minio bucket after clearing existing files in the path,
        ensuring the bucket and folder structure exist.

        :param bucket_name: Name of the Minio bucket.
        :param user_id: User ID as part of the object path.
        :param label: Label as part of the object path.
        :param directory_path: Path of the local directory to upload.
        """
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

        path_prefix = f"{user_id}/{label}/"

        existing_objects = self.client.list_objects(bucket_name, prefix=path_prefix, recursive=True)
        for obj in existing_objects:
            self.client.remove_object(bucket_name, obj.object_name)
            print(f"Deleted {obj.object_name} from bucket {bucket_name}")

        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory_path)
                object_name = f"{path_prefix}{relative_path.replace(os.path.sep, '/')}"
                self.client.fput_object(bucket_name, object_name, file_path)
                print(f"Uploaded {file_path} to {object_name} in bucket {bucket_name}")

