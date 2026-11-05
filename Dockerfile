FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    LIBGL_ALWAYS_SOFTWARE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential pkg-config git \
        ffmpeg xvfb xauth \
        libgl1 libgl1-mesa-dri libglu1-mesa libegl1 libglx-mesa0 \
        libpango1.0-dev libcairo2-dev libglib2.0-dev \
        fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir manimgl

WORKDIR /manim
