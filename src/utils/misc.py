from zoneinfo import ZoneInfo
from django.utils import timezone
import requests
import base64
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import logging
from common.exceptions import InvalidInputError
from utils.minio_utils import MinioUtil

logger = logging.getLogger('app')
utc_timezone = ZoneInfo('UTC')


def naive_utc_datetime_to_local_timezone(date_time):
    """
    convert naive datetime in UTC to local timezone-aware datetime. Using for getting datetime from mongodb.
    :param date_time: naive datetime object
    """
    return timezone.localtime(timezone.make_aware(date_time, timezone=utc_timezone))

def datetime_to_local_timezone(date_time):
    """
    convert datetime to local time-zone which set in settings.TIME_ZONE
    :param date_time: naive or timezone-aware datetime
    """
    if date_time.tzinfo is not None and date_time.tzinfo.utcoffset(date_time) is not None:
        # Already timezone-aware
        return timezone.localtime(date_time)
    else:
        # Set the default timezone
        return timezone.make_aware(date_time)


def get_current_date():
    return timezone.now().date()


def datetime_iso_format(aware_datetime):
    return aware_datetime.isoformat() + 'Z'


def get_bytes_from_remote_file(url):
    res = requests.get(url)
    return res.content, res.status_code

def get_image_extension(fmt):
    if fmt == 'JPEG':
        return 'jpg'
    return fmt.lower()


def convert_base64_string_to_bytes(base64_string):
    return base64.decodebytes(base64_string.encode())


def convert_bytes_to_base64_string(bytes_data):
    return base64.encodebytes(bytes_data).decode()


class TaskResult:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error


def run_concurrent_tasks(task_handler, list_args, max_workers=4, timeout=None):
    task_name = getattr(task_handler, '__name__', '')
    results = []
    executor = ThreadPoolExecutor(max_workers=max_workers)
    try:
        tasks = [executor.submit(task_handler, *args) for args in list_args]
        for task in tasks:
            try:
                res = task.result(timeout=timeout)
                task_result = TaskResult(result=res)
            except FutureTimeoutError:
                new_exception = FutureTimeoutError(f'Timeout to run {task_name} after {timeout}s')
                task_result = TaskResult(error=new_exception)
            except Exception as ex:
                task_result = TaskResult(error=ex)
                logger.exception(ex)
            results.append(task_result)

        return results
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def run_concurrent_separate_tasks(list_tasks, max_workers=4, timeout=None):
    results = []
    executor = ThreadPoolExecutor(max_workers=max_workers)
    try:
        tasks = []
        for task_info in list_tasks:
            task_func = task_info[0]
            task_args = task_info[1:]
            tasks.append(executor.submit(task_func, *task_args))

        for task in tasks:
            try:
                res = task.result(timeout=timeout)
                task_result = TaskResult(result=res)
            except FutureTimeoutError:
                task_result = TaskResult(error=FutureTimeoutError('Timeout to run task'))
            except Exception as ex:
                task_result = TaskResult(error=ex)
            results.append(task_result)

        return results
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def wrap_run_concurrent_separate_tasks(list_tasks, max_workers=4, timeout=None):
    list_task_results = run_concurrent_separate_tasks(list_tasks, max_workers, timeout)
    results = []
    for task_result in list_task_results:
        if task_result.error:
            logger.error(task_result.error)
            results.append(None)
        else:
            results.append(task_result.result)

    return results


def convert_wildcard_to_regex(text):
    text = text.replace(' ', '')
    if not text:
        return ''

    output = text

    if output[0] == '*':
        output = output[1:]
    else:
        output = '^' + output

    if not output:
        return ''

    if output[-1] == '*':
        output = output[:-1]
    else:
        output = output + '$'

    return output.replace('*', '.*')


def convert_list_wildcard_to_regex(patterns):
    if not patterns:
        return []

    first = patterns[0]
    outputs = convert_wildcard_to_regex(first)
    for p in patterns[1:]:
        outputs += '|' + convert_wildcard_to_regex(p)
    return outputs


def parse_sort_params(params):
    try:
        fields = params.split(',')
        orders = []
        for field in fields:
            tokens = field.split(':')
            if tokens[1] == 'asc':
                orders.append(tokens[0])
            elif tokens[1] == 'desc':
                orders.append('-' + tokens[0])
        return orders
    except Exception as ex:
        logger.error(ex)
        raise InvalidInputError({'sort': 'Invalid sort params'})


def can_search_by_reversed_text(glob_pattern):
    """
    pattern: "*abcd", "*a*bc" => True
    """
    if glob_pattern[0] == '*' and glob_pattern[-1] != '*':
        return True
    else:
        return False


def can_search_by_reversed_text_v2(glob_pattern: str):
    """
    pattern: *a, a*bc => True
    pattern: ab, a*, *a*, ab*c => False
    """
    if glob_pattern[-1] == '*':
        # pattern: xxx*
        return False

    # current pattern: xxxa
    if glob_pattern[0] == '*':
        # pattern: *xxa
        return True

    # current pattern: axxxa
    left = glob_pattern.find('*')
    if left < 0:
        return False
    right = glob_pattern.rfind('*')
    if right < 0:
        return False
    if len(glob_pattern) - right - 1 > left:
        return True
    return False


def get_file_anywhere(file_path):
    # return bytes data
    # this is a local file
    if file_path.startswith('file://'):
        file_path = file_path.replace('file://', '')
        with open(file_path, 'rb') as f:
            return f.read()

    if file_path.startswith('s3://'):
        try:
            file_path = file_path[5:]
            index = file_path.find('/')
            bucket = file_path[:index]
            object_name = file_path[index + 1:]
        except Exception:
            raise ValueError('Invalid s3 file path')
        return MinioUtil.get_object_with_bucket(bucket, object_name)

    # remote url
    data, _ = get_bytes_from_remote_file(file_path)
    return data

def get_base64_from_file(file_path):
    data = get_file_anywhere(file_path)
    return base64.b64encode(data).decode('utf-8')
