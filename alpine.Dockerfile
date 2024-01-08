FROM node:20.10.0-alpine
RUN apk update && \
    apk add vim && \
    apk add py3-pip && \
    rm -rf /var/cache/apk/* && \
    rm /usr/lib/python3.11/EXTERNALLY-MANAGED && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir PySimpleGUI

