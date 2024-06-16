import base64
import json
import pika
import time
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from common.config import settings
from common.clients.amqp import Session
import app.monitoring as monitoring
from app.pipeline import VideoProcessing
import logging

#logging.getLogger("pyscenedetect").setLevel(level=logging.ERROR)

session = Session()
session.set_connection_params(
    host=str(settings.rabbitmq.host),
    port=settings.rabbitmq.port,
    virtual_host=settings.rabbitmq.virtual_host,
    username=settings.rabbitmq.username,
    password=settings.rabbitmq.password,
)

pipeline = VideoProcessing()


def deserialize(encoded_string):
    return base64.b64decode(encoded_string)


@session.on_message
def on_message(channel: BlockingChannel, method: Basic.Deliver,
               properties: pika.BasicProperties, body: bytes):
    monitoring.timer.start('preprocessing')

    start = time.time()
    value = json.loads(body.decode().replace("'", '"'))
    id = value['uuid']
    print(f"Going to process {id}")
    file_path = f"binary_{id}.mp4"
    chunk = value['serialized_chunk']
    chunk = deserialize(chunk)

    with open(file_path, 'wb') as wfile:
        wfile.write(chunk)

    monitoring.processing_duration_seconds.labels('preprocessing')\
        .observe(monitoring.timer.get('preprocessing'))
    monitoring.timer.start('inference')

    embs = pipeline.run(file_path)
    print(f"FOR VIDEO {id} GOT {len(embs)} VECTORS FOR {round(time.time() - start)} seconds")

    for emb in embs:
        send = {
            "uuid": id,
            "model": settings.encoder.encoder,
            "encoded_chunk": emb.tolist()
        }
        session.publish(
            exchange="",
            routing_key=settings.rabbitmq.video_queue,
            body=json.dumps(send),
            properties=pika.BasicProperties(
                content_type='application/json'
            )
        )

    monitoring.processing_duration_seconds.labels('inference')\
        .observe(monitoring.timer.get('inference'))
    monitoring.timer.start('publishing')

    channel.basic_ack(delivery_tag=method.delivery_tag)

    monitoring.processing_duration_seconds.labels('publishing')\
        .observe(monitoring.timer.get('publishing'))
    monitoring.messages_processed_total.inc()


def main():
    session.start_consuming(
        settings.rabbitmq.queue,
        prefetch_count=settings.rabbitmq.prefetch_count
    )
