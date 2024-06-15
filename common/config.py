from pathlib import Path
import os

from pydantic import (
    BaseModel,
    BaseSettings,
    PositiveInt
)


basedir = Path(__file__).parent.parent.absolute()


class MonitoringSettings(BaseModel):
    hostname: str = "http://grafana.mutagen.space"
    namespace: str = "processing"
    port: int = 9010


class EncoderSettings(BaseModel):
    encoder: str = "jinaai/jina-clip-v1"
    sample_frames: int = 4
    sim_threshold: float = 0.85


class DecoderSettings(BaseModel):
    decoder: str = "vit_base"
    path_size: int = 16
    feature: str = "k"
    k_patches: int = 100
    dbscan_eps: int = 3


class RabbitMQSettings(BaseModel):
    host: str = 'rabbitmq.mutagen.space'
    port: PositiveInt = 5672
    virtual_host: str = '/'
    username: str = 'processing'
    password: str = '!U%wWa8L)9kJeJ&'

    queue: str = 'video_chunks'
    audio_queue: str = 'audio_emb'
    face_queue: str = 'face_emb'
    video_queue: str = 'video_emb'
    audio_chunks_queue: str = "audio_chunks"

    prefetch_count: PositiveInt = int(os.environ['RABBITMQ__PREFETCH_COUNT'])
    print(f"Prefetch count = {prefetch_count}")


class Settings(BaseSettings):
    encoder: EncoderSettings = EncoderSettings()
    decoder: DecoderSettings = DecoderSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    monitoring: MonitoringSettings = MonitoringSettings()

    class Config:
        env_nested_delimiter = '__'


settings = Settings()
