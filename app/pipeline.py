from PIL import Image
import numpy as np
from numpy.linalg import norm
from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
from transformers import AutoModel
from decord import VideoReader, cpu
import torch
import os
import glob
np.random.seed(0)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


CLIP_MODEL = 'jinaai/jina-clip-v1'
SAMPLE_FRAMES = 4
SIM_THRESHOLD = 0.85


def sample_frame_indices(clip_len, seg_len):
    #TODO переписать на более рандомный селекшион фреймов
    frame_sample_rate = seg_len // clip_len
    converted_len = int(clip_len * frame_sample_rate)
    end_idx = np.random.randint(frame_sample_rate, seg_len)
    start_idx = end_idx - converted_len - 1
    indices = np.linspace(start_idx, end_idx, num=clip_len)
    indices = np.clip(indices, start_idx, end_idx - 1).astype(np.int64)
    return indices


def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))


class VideoProcessing:

    def __init__(self):
        self.clip = AutoModel.from_pretrained(CLIP_MODEL, trust_remote_code=True).to(device)

    def __split(self, video_path):

        scene_list = detect(video_path, AdaptiveDetector())
        split_video_ffmpeg(video_path, scene_list)

    def __scene_batching(self):

        for name in glob.glob("*.mp4"):
            vr = VideoReader(name, ctx=cpu(0))

            # sample frames
            vr.seek(0)
            indices = sample_frame_indices(clip_len=SAMPLE_FRAMES, seg_len=len(vr))
            video = vr.get_batch(indices).asnumpy()[:-1]
            os.remove(name)

            yield video

    def process_one_scene_frames(self, sample_frames):
        return np.mean(np.array([self.clip.encode_image(Image.fromarray(i)) for i in sample_frames]), axis=0)

    def add_detection(self, new_emb):
        for old_emb in self.embs:
            sim = cosine_similarity(old_emb, new_emb)
            if sim >= SIM_THRESHOLD:
                break
        self.embs.append(new_emb)

    def run(self, video_path):
        self.embs = []

        self.__split(video_path)
        for scene in self.__scene_batching():
            self.embs.append(self.process_one_scene_frames(scene))

        return self.embs
