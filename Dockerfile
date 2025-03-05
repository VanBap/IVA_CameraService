# base image
FROM python:3.10.8 AS base
RUN adduser --system --group bigdata
ENV PYTHONUNBUFFERED=1

# install ntp, opencv
RUN ln -fs /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
  && apt-get install -y --no-install-recommends default-libmysqlclient-dev default-mysql-client ffmpeg  \
     htop net-tools ntp telnet vim \
  && apt-get clean

RUN mkdir -p /home/bigdata/src
WORKDIR /home/bigdata
COPY requirements.txt /home/bigdata

# install dependencies
FROM base AS dependencies
RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt

# clean temporary files
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# setup all configuration
FROM dependencies AS config

FROM config AS development
# deploy code
WORKDIR /home/bigdata/src
COPY src .

EXPOSE 8080

USER bigdata
CMD ["sh", "-c", "PYTHONIOENCODING='UTF-8' ./start_gunicorn.sh"]
