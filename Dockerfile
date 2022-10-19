FROM ubuntu:22.04

# docker build -t ghcr.io/buildsi/splice-experiment-results .

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 \
    python3-pip \
    git \
    perl \
    vim \
    sqlite3
    
# This will ignore the data folder, which should be bound at runtime
WORKDIR /code
COPY . /code
RUN pip install -r /code/requirements.txt && \
    # Nice to have for interactive development
    pip install IPython

