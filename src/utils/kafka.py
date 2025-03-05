import kafka # noqa
import threading
import json
import logging
from api import settings
from common.exceptions import ApplicationError

lock = threading.Lock()
logger = logging.getLogger('app')
default_kafka_producer = None


def create_kafka_producer(bootstrap_servers):
    global default_kafka_producer
    with lock:
        if default_kafka_producer:
            return default_kafka_producer

        try:
            default_kafka_producer = kafka.KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                acks='all',
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            logger.info('Created Kafka Producer to %s', bootstrap_servers)
            return default_kafka_producer
        except kafka.errors.KafkaError as ex:  # noqa
            logger.exception(ex)
            return None

# pre-init
create_kafka_producer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVER)


def send_to_kafka(topic, value, key=None):
    kafka_producer = create_kafka_producer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVER)
    if not kafka_producer:
        raise ApplicationError('Kafka producer has not yet connected to brokers')

    return kafka_producer.send(topic, value=value, key=key)
