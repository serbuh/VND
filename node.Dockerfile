FROM node:20-slim
RUN apt update && \
    apt install -y vim && \
    apt install -y pip && \
    apt install -y git && \
    apt clean && rm -rf /var/lib/apt/lists/* && \
    rm /usr/lib/python3.11/EXTERNALLY-MANAGED && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir PySimpleGUI

