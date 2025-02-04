FROM docker.io/library/python:3.11-slim 
# Must be an image with glibc
RUN apt update
RUN apt upgrade -y
RUN apt install -y tzdata 
WORKDIR /srv/app
COPY webapp/requirements.txt /srv/app/requirements.txt
RUN python -m venv /srv/app/env --system-site-packages
RUN /srv/app/env/bin/python -m pip install -r /srv/app/requirements.txt
COPY webapp /srv/app
ENV TZ=Europe/Berlin
ENV PYTHONIOENCODING UTF-8
EXPOSE 5000
CMD [ "/srv/app/env/bin/python", "/srv/app/app.py" ]