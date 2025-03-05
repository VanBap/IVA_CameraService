from ..models import Camera
from . import config
from urllib.parse import urlparse, quote


def normalize_url(url):
    obj = urlparse(url)
    if not obj.username or not obj.password:
        return url

    username = quote(obj.username)
    password = quote(obj.password)
    replaced = obj._replace(netloc="{}:{}@{}".format(username, password, obj.hostname)) # noqa
    return replaced.geturl()


def get_url_for_detector(camera_data):
    if isinstance(camera_data, Camera):
        if camera_data.main_restream:
            return camera_data.main_restream
        if camera_data.main_stream:
            return camera_data.main_stream
        if camera_data.url:
            return camera_data.url
        return None

    if camera_data.get('main_restream'):
        return camera_data.get('main_restream')
    if camera_data.get('main_stream'):
        return camera_data.get('main_stream')
    if camera_data.get('url'):
        return camera_data.get('url')
    return None


def get_norm_url_for_detector(camera_data):
    url = get_url_for_detector(camera_data)
    return normalize_url(url) if url else None


def validate_areas(areas):
    if not isinstance(areas, list):
        return
