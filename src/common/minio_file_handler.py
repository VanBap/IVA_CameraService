import datetime
import logging
import os
import time
from io import BytesIO
import string
import shortuuid
# sanitize_filename: from pathvalidate import sanitize_filename
from django.core.files.uploadedfile import UploadedFile
from django.core.files.uploadhandler import FileUploadHandler
from minio import Minio

from .exceptions import ApplicationError
from api import settings

logger = logging.getLogger('app')
alphabet = string.ascii_lowercase + string.digits
su = shortuuid.ShortUUID(alphabet=alphabet)

minio_client = Minio(settings.MINIO['internal_host'],
                     access_key=settings.MINIO['access_key'],
                     secret_key=settings.MINIO['secret_key'],
                     secure=settings.MINIO['secure'])


class MinioUploadedFile(UploadedFile):
    def __init__(self, file, field_name, name, content_type, size, charset,
                 content_type_extra=None, object_name='', relative_object_name=''):
        super().__init__(file, name, content_type, size, charset, content_type_extra)
        self.field_name = field_name
        self.object_name = object_name
        self.relative_object_name = relative_object_name

    def __str__(self):
        return self.name


class MinioUploadedFileHandler(FileUploadHandler):
    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.file = BytesIO() # noqa

    def receive_data_chunk(self, raw_data, start):
        self.file.write(raw_data)

    def generate_object_name(self, file_name): # noqa
        # upload to minio
        now = datetime.datetime.now()
        middle_path = '{}/{:02d}/{:02d}'.format(now.year, now.month, now.day)
        _, source_ext = os.path.splitext(os.path.basename(file_name))
        # can be used: source_basename_no_ext = sanitize_filename(source_basename_no_ext)
        dest_filename = "{}-{}{}".format(round(time.time() * 1000), su.random(length=6), source_ext)
        relative_object_name = os.path.join(middle_path, dest_filename)
        obj_name = os.path.join(settings.MINIO['root_uploads'], relative_object_name)
        return obj_name, relative_object_name

    def file_complete(self, file_size):
        self.file.seek(0)

        # check if bucket exists
        bucket = os.getenv('MINIO_BUCKET')
        if not minio_client.bucket_exists(bucket):
            raise ApplicationError('Bucket not exist')

        # upload to minio
        obj_name, relative_object_name = self.generate_object_name(self.file_name)

        minio_client.put_object(bucket, obj_name, self.file, file_size)
        logger.info(f'Upload minio done, origin {self.file_name}, obj {obj_name}')

        return MinioUploadedFile(
            file=self.file,
            field_name=self.field_name,
            name=self.file_name,
            content_type=self.content_type,
            size=file_size,
            charset=self.charset,
            content_type_extra=self.content_type_extra,
            object_name=obj_name,
            relative_object_name=relative_object_name
        )
