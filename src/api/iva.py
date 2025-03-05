import os
import logging
from pymongo import monitoring
from urllib.parse import urlparse

mongo_logger = logging.getLogger('mongo')
logger = logging.getLogger('app')


class CommandLogger(monitoring.CommandListener):

    def started(self, event):
        mongo_logger.debug("Run command {0.command} with request id {0.request_id}".format(event))

    def succeeded(self, event):
        mongo_logger.info("Finish request {} in {} s".format(event.request_id, event.duration_micros / 1e6))

    def failed(self, event):
        mongo_logger.info("Fail request {} in {} s".format(event.request_id, event.duration_micros / 1e6))


def register_mongo_monitor():
    monitoring.register(CommandLogger())


def parse_cors_allowed_string():
    text = os.getenv('CORS_ALLOWED_ORIGINS')
    if not text:
        return []
    return text.split(',')


def bool_env(text: str):
    if not text:
        return False
    text = text.lower()
    if text == '0' or text == 'false' or text == 'no' or text == 'n':
        return False
    elif text == '1' or text == 'true' or text == 'yes' or text == 'y':
        return True
    else:
        raise ValueError(f'Invalid boolean ENV: {text}')


def parse_redis_sentinel_config(redis_sentinel_config):
    """
    config: "node-1:26379,node-2:26379,node-3:26379"
    """
    try:
        list_sentinels = redis_sentinel_config.split(',')
        results = []
        for sentinel in list_sentinels:
            fields = sentinel.split(':')
            results.append((fields[0], int(fields[1])))

        return results
    except Exception as ex:
        logger.exception(ex)
        raise ValueError(f'Invalid redis sentinel config: {redis_sentinel_config}')


def get_minio_config_from_env():
    internal_endpoint = os.getenv('MINIO_INTERNAL_ENDPOINT')
    if internal_endpoint:
        print('Use MINIO_INTERNAL_ENDPOINT')
        # new config, support https
        # use 2 env MINIO_INTERNAL_ENDPOINT and MINIO_PUBLIC_ENDPOINT
        url_obj = urlparse(internal_endpoint)
        config = {
            'internal_host': url_obj.netloc,  # domain.com:8000 (for minio-py)
            'secure': url_obj.scheme == 'https',  # for minio-py
            'internal_endpoint': url_obj.scheme + '://' + url_obj.netloc,  # https://domain.com:8000
        }
        # ENV MINIO_PUBLIC_ENDPOINT = '' -> internal url (bucket url: http://local_ip:port/iva/)
        # ENV MINIO_PUBLIC_ENDPOINT = '/' -> relative url (bucket url: /iva/)
        # ENV MINIO_PUBLIC_ENDPOINT = 'https://domain.com' -> absolute url (bucket url: https://domain.com/iva/)
        config['public_endpoint'] = os.getenv('MINIO_PUBLIC_ENDPOINT') or config['internal_endpoint']
    else:
        print('Use MINIO_HOST')
        # old config (not support https)
        # use MINIO_HOST, MINIO_PORT, MINIO_HOST_FRONTEND
        default_protocol = 'http'
        config = {
            'internal_host': os.getenv('MINIO_HOST') + ':' + os.getenv('MINIO_PORT'),  # for minio-py
            'secure': False,
            'internal_endpoint': f'{default_protocol}://' + os.getenv('MINIO_HOST') + ':' + os.getenv('MINIO_PORT'),
        }

        # minio public url
        # ENV MINIO_HOST_FRONTEND = '' -> internal url (http://local_ip:port/iva/)
        # ENV MINIO_HOST_FRONTEND = '/' -> relative url (/iva/)
        # ENV MINIO_HOST_FRONTEND = 'https://domain.com' -> absolute url (https://domain.com/iva/)
        config['public_endpoint'] = os.getenv('MINIO_HOST_FRONTEND') or config['internal_endpoint']

    # others config
    config.update({
        'access_key': os.getenv('MINIO_ACCESS_KEY'),
        'secret_key': os.getenv('MINIO_SECRET_KEY'),
        'bucket': os.getenv('MINIO_BUCKET'),
        'signature_version': 's3v4',
        'region_name': 'ap-southeast-1',
        'root_dossier': 'dossier',
        'root_uploads': 'uploads',
    })

    return config


def parse_mk_mapping_category_rule(env_string):
    """
    env_string: "11:5,12:400"
    return: dict {iva_category_id -> rule_id}
    """
    if not env_string:
        return {}

    try:
        items = env_string.split(',')
        results = {}
        for item in items:
            fields = item.split(':')
            iva_category_id = int(fields[0])
            iva_rule_id = int(fields[1])
            results[iva_category_id] = iva_rule_id

        return results
    except Exception as ex:
        raise ValueError('Invalid MK mapping rule config') from ex
