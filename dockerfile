FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-devel

RUN apt update -y  && apt install -y --no-install-recommends \
    libsamplerate0 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /workspace


RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ fairseq streamlit python-dotenv scipy faiss-cpu pyworld onnxruntime av==11.0.0 ffmpeg-python PyYAML torchcrepe onnxruntime-gpu soundfile praat-parselmouth librosa
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ audio-separator[gpu]
RUN pip install --no-cache-dir -i tensorboardX samplerate 

EXPOSE 22222


# 视频服务
CMD ["streamlit", "run", "video_morph_web.py", "--server.port=22222", "--server.maxUploadSize=1000"]