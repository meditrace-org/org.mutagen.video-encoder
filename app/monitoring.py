import time

from prometheus_client import (
    CollectorRegistry,
    start_http_server,
    Summary,
    Counter,
)

from common.config import settings


HOSTNAME = settings.monitoring.hostname
NAMESPACE = settings.monitoring.namespace
start_http_server(settings.monitoring.port)


class Timer:
    def __init__(self):
        self.start_times = {}

    def start(self, name):
        self.start_times[name] = time.perf_counter()

    def get(self, name):
        return time.perf_counter() - self.start_times[name]


timer = Timer()


registry = CollectorRegistry()


processing_duration_seconds = Summary(
    name='processing_duration_seconds',
    documentation='Duration of processing stages',
    namespace=NAMESPACE,
    labelnames=['stage'],
    registry=registry,
)

messages_processed_total = Counter(
    name='messages_processed_total',
    documentation='Total number of processed messages',
    namespace=NAMESPACE,
    labelnames=[],
    registry=registry,
)
