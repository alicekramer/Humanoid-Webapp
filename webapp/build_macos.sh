#!/bin/sh
podman build -t nao --arch amd64 .
podman run -it --rm -e NAO_IP=10.2.100.61 -p 5001:5000 nao