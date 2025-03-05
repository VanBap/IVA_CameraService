from telegraf.client import TelegrafClient
from django.conf import settings


client = TelegrafClient(
    host=settings.TELEGRAF_HOST,
    port=settings.TELEGRAF_PORT,
    tags={
        'service': settings.SERVICE_NAME,
    }
)


def send_metric(metrics, tags=None, timestamp=None):
    """
    metrics: dict [metric_name: metric_value]
    all metrics of all services will be saved in one bucket in DB (measurement_name, tag sets, metric_1, metric_2,...)
    Note: in method client.metric(), values could be a single value or dict of value_name: value pairs.
    When value is a single value, value_name will be string "value"
    """
    client.metric(
        measurement_name=settings.SERVICE_NAME,
        values=metrics,
        tags=tags,
        timestamp=timestamp,
    )
