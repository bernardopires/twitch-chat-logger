FROM postgres:latest
ADD scripts /docker-entrypoint-initdb.d
ADD . /files
WORKDIR /files
