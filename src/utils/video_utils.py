import ffmpeg  # noqa
import logging
import os

logger = logging.getLogger('app')


class MediaFileError(Exception):
    pass


class MediaFileType:
    IMAGE = 1
    VIDEO = 2


# jpeg, webp => image2, jpeg => jpeg_pipe, png => png_pipe, bmp => bmp_pipe
FFMPEG_IMAGE_FORMATS = ['image2', 'jpeg_pipe', 'png_pipe', 'bmp_pipe']


def get_media_type_from_format_name(format_name):
    for name in FFMPEG_IMAGE_FORMATS:
        if format_name == name:
            return MediaFileType.IMAGE
    return MediaFileType.VIDEO


def get_video_metadata(file_path):
    try:
        probe = ffmpeg.probe(file_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is None:
            return {}

        width = int(video_stream['width'])
        height = int(video_stream['height'])

        return {
            'width': width,
            'height': height
        }
    except Exception as ex:
        logger.error(ex)
        return {}


def get_media_info(file_path):
    video_info = {}
    try:
        probe = ffmpeg.probe(file_path, hide_banner=None)
    except ffmpeg.Error as ex:
        stderr = ex.stderr.decode()
        raise MediaFileError(stderr) from ex

    # format
    fmt = probe['format']
    video_info['format_name'] = fmt['format_name']
    video_info['media_type'] = get_media_type_from_format_name(fmt['format_name'])

    video_info['duration'] = float(fmt['duration']) if 'duration' in fmt else None
    video_info['file_size'] = int(fmt['size']) if 'size' in fmt else None
    video_info['bit_rate'] = int(fmt['bit_rate']) if 'bit_rate' in fmt else None

    # video
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream:
        video_info['width'] = int(video_stream['width'])
        video_info['height'] = int(video_stream['height'])
        video_info['codec_name'] = video_stream['codec_name']

    return video_info


def extract_thumbnail(video_file_path, thumbnail_file_path='', capture_time=0, is_video=True, print_cmd_output=False):
    try:
        if is_video:
            pipeline = ffmpeg.input(video_file_path, ss=capture_time, skip_frame='nokey')
        else:
            pipeline = ffmpeg.input(video_file_path)

        if thumbnail_file_path:
            # write to file
            pipeline = pipeline.output(thumbnail_file_path, vframes=1)
        else:
            # write to bytes
            pipeline = pipeline.output('pipe:', vframes=1, format='image2', vcodec='mjpeg')

        # run
        log_level = 'debug' if print_cmd_output else 'warning'
        out_bytes, stdout = (
            pipeline
            .global_args('-loglevel', log_level)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        if print_cmd_output:
            logger.info(stdout)

        if thumbnail_file_path:
            if os.path.isfile(thumbnail_file_path):
                return thumbnail_file_path
        elif out_bytes:
            return out_bytes

        raise MediaFileError(f'Output data is empty. Detail log: f{stdout}')

    except ffmpeg.Error as ex:
        raise MediaFileError(ex.stderr.decode()) from ex
