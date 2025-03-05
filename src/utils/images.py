import io
from PIL import Image


def get_image_format_from_data(data: bytes):
    try:
        img = Image.open(io.BytesIO(data))
        return img.format
    except Exception: # noqa
        return None
