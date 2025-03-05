import logging
from django.core.management.base import BaseCommand
from utils import misc

logger = logging.getLogger('app')


def main():
    try:
        data1 = misc.get_file_anywhere('http://10.124.71.97:11015/iva/uploads/2024/12/11/1733892403722-279eqd.jpg')
        logger.info('Get data1 done, length %s, data %s', len(data1), data1[:20])
    except Exception as ex:
        logger.exception('Failed to get image 1: %s', ex)

    try:
        data2 = misc.get_file_anywhere('file:///home/shang/test3.jpg')
        logger.info('Get data2 done, length %s, data %s', len(data2), data2[:20])
    except Exception as ex:
        logger.exception('Failed to get image 2: %s', ex)

    try:
        data3 = misc.get_file_anywhere('s3://iva-dev/uploads/2024/12/11/1733894887367-274e8j.jpg')
        logger.info('Get data3 done, length %s, data %s', len(data3), data3[:20])
    except Exception as ex:
        logger.exception('Failed to get image 3: %s', ex)


class Command(BaseCommand):
    help = 'Test'

    def handle(self, *args, **options):
        main()
