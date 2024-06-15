FROM huggingface/transformers-inference:4.24.0-pt1.13-cpu

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