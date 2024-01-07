FROM node:20
RUN apt update && \
    apt install -y pip && \
    apt clean && rm -rf /var/lib/apt/lists/* && \
    rm /usr/lib/python3.11/EXTERNALLY-MANAGED && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir PySimpleGUI

