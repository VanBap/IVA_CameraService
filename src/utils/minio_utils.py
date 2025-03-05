import datetime
import io
import logging
import os
import string
import time
from urllib.parse import urljoin
from zipfile import ZipFile
from pathvalidate import sanitize_filepath
import shortuuid
from minio import Minio
import base64
from minio.commonconfig import CopySource
import requests
from api import settings
from . import images as image_utils
from common.exceptions import ImageInvalid

alphabet = string.ascii_lowercase + string.digits
su = shortuuid.ShortUUID(alphabet=alphabet)

logger = logging.getLogger('app')
minio_client = Minio(settings.MINIO['internal_host'],
                     access_key=settings.MINIO['access_key'],
                     secret_key=settings.MINIO['secret_key'],
                     secure=settings.MINIO['secure'])

MINIO_BUCKET = settings.MINIO['bucket']
MINIO_PUBLIC_BUCKET_URL = os.path.join(settings.MINIO['public_endpoint'], MINIO_BUCKET) + '/'
HTTP_PREFIX = 'http'
HTTPS_PREFIX = 'https'


class MinioUtil:
    @staticmethod
    def get_object(object_name):
        res = minio_client.get_object(MINIO_BUCKET, object_name)
        if res.status != 200:
            return None
        return res.read()

    @staticmethod
    def get_object_with_bucket(bucket, object_name):
        res = minio_client.get_object(bucket, object_name)
        if res.status != 200:
            return None
        return res.read()

    @staticmethod
    def copy_object(source_object_name, dest_object_name):
        minio_client.copy_object(MINIO_BUCKET, dest_object_name, CopySource(MINIO_BUCKET, source_object_name))

    @staticmethod
    def upload_local_file(local_file_path, root_folder):
        obj_name = MinioUtil.generate_path(root_folder, basename=os.path.basename(local_file_path))

        with open(local_file_path, 'rb') as file_data:
            file_stat = os.stat(local_file_path)
            minio_client.put_object(MINIO_BUCKET, obj_name, file_data, file_stat.st_size)
            logger.info(f'Upload local file {local_file_path} to minio {obj_name}')
            return obj_name

    @staticmethod
    def upload_remote_file(remote_file_path, root_folder, check_status_code=True, check_image=False, fetch_timeout=30):
        obj_name = MinioUtil.generate_path(root_folder, basename=os.path.basename(remote_file_path))
        t1 = time.time()
        # get file data
        res = requests.get(remote_file_path, timeout=fetch_timeout)
        if check_status_code and res.status_code >= 400:
            raise requests.exceptions.RequestException('Request failed with status code {}'.format(res.status_code))
        file_content = res.content  # bytes
        t2 = time.time()

        # check data format
        if check_image and not image_utils.get_image_format_from_data(file_content):
            raise ImageInvalid()

        minio_client.put_object(MINIO_BUCKET, obj_name, io.BytesIO(file_content), len(file_content))
        t3 = time.time()
        logger.info('Upload remote file {} to minio {}: fetch {:.2f}s, upload {:.2f}s'.format(
            remote_file_path, obj_name, t2 - t1, t3 - t2))
        return obj_name

    @staticmethod
    def put_object(object_name, data, length):
        minio_client.put_object(MINIO_BUCKET, object_name, data, length)

    @staticmethod
    def get_absolute_url(object_path):
        if object_path:
            if object_path.startswith(HTTP_PREFIX) or object_path.startswith(HTTPS_PREFIX):
                return object_path
            return MINIO_PUBLIC_BUCKET_URL + object_path
        return None

    @staticmethod
    def normalize_url(url: str):
        if not url:
            return ''

        if url.startswith('/'):
            # relative link, url is a path
            return urljoin(settings.MINIO['internal_endpoint'], url)
        else:
            return url

    @staticmethod
    def generate_path(root_folder, basename=''):
        source_name = str(round(time.time() * 1000))
        source_ext = ''
        if basename:
            original_source_name, source_ext = os.path.splitext(basename)
            if original_source_name != '*':
                source_name = original_source_name

        now = datetime.datetime.now()
        middle_path = '{}/{:02d}/{:02d}'.format(now.year, now.month, now.day)
        dest_filename = "{}_{}{}".format(source_name, su.random(length=6), source_ext)
        relative_object_name = os.path.join(middle_path, dest_filename)
        obj_name = os.path.join(root_folder, relative_object_name)
        return obj_name

    @staticmethod
    def put_file(local_file_path, object_name):
        minio_client.fput_object(MINIO_BUCKET, object_name, local_file_path)

    @staticmethod
    def upload_base64_image_data(base64_image, root_folder, basename):
        if base64_image is None:
            return None

        try:
            fields = base64_image.split(',')
            if len(fields) == 2:
                # data:image/png;base64,iVBORw0KGgoANSUhEUgAA..."
                imgdata = base64.b64decode(base64_image.split(',')[1])
            else:
                imgdata = base64.b64decode(base64_image)
        except Exception as ex:
            logger.exception(ex)
            raise ex

        dest_object_name = MinioUtil.generate_path(root_folder, basename=basename)
        MinioUtil.put_object(dest_object_name, io.BytesIO(imgdata), len(imgdata))
        return dest_object_name

    @staticmethod
    def upload_file(url, root_folder, check_status_code=True, check_image=False, fetch_timeout=30):
        url = MinioUtil.normalize_url(url)
        return MinioUtil.upload_remote_file(url, root_folder,
                                            check_status_code=check_status_code,
                                            check_image=check_image, fetch_timeout=fetch_timeout)


def minio_compress_list_files2(files):
    list_file_contents = []
    list_file_names = []
    for file in files:
        file_name = file.split('/')[-1]
        file_content = MinioUtil.get_object(file)

        list_file_names.append(file_name)
        list_file_contents.append(file_content)

    content = io.BytesIO()
    with ZipFile(content, 'w') as zip_obj:
        for name, data in zip(list_file_names, list_file_contents):
            zip_obj.writestr(name, data)

    return content


def minio_compress_list_files(list_file_infos):
    """
    input: [
        {
            'zip_folder': 'Station 1/2023-01-12T12-05-09',
            'object_names': [list of minio object path]
        }
    ]
    """
    content = io.BytesIO()
    with ZipFile(content, 'w') as zip_obj:
        for info in list_file_infos:
            folder_name = info['zip_folder']
            list_file_paths = info['object_names']
            for file_path in list_file_paths:
                file_data = MinioUtil.get_object(file_path)
                try:
                    file_name = file_path.split('/')[-1]
                except Exception as ex:
                    logger.exception(ex)
                    file_name = 'file'

                # write to zip file
                zip_path = sanitize_filepath(os.path.join(folder_name, file_name)) # noqa
                zip_obj.writestr(zip_path, file_data)

    return content
