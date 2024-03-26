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
