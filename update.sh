#!/bin/sh
GIT_SSL_NO_VERIFY=true git pull
sudo docker compose up -d --build