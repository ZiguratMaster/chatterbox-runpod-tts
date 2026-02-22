FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

RUN apt-get update && apt-get install -y ffmpeg espeak-ng wget && apt-get clean

# TTS sin compilación (conda env)
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH="/opt/conda/bin:$PATH"
RUN conda install -c conda-forge pytorch==2.4.0 pytorch-cuda=12.4 -y && \
    pip install TTS==0.22.0 runpod librosa soundfile pydub numpy

COPY handler.py /handler.py
COPY audio_ref_es.wav /vol/audio_ref_es.wav

CMD ["python", "/handler.py"]