#!/bin/sh
rsync -avP . nao@10.2.100.61:alice_nao --exclude=.git --exclude=vendor --exclude=venv
# on Host:
cd alice_nao
python -m virtualenv venv
source venv/bin/activate