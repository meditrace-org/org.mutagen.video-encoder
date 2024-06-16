FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

#set up environment
RUN apt-get update \
    && apt-get install ffmpeg libsm6 libxext6  -y \
    && apt-get install -y python3 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /home

COPY ./requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY / .

CMD ["python3", "-m", "app"]