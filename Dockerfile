# Dockerfile specifically for python3
FROM python:3-wheezy

# You can do python version this way (uncomment to configure):
# RUN apt-install python3-minimal
# RUN ln -s python3 /usr/bin/python

# See http://wiki.postgresql.org/wiki/Apt
ENV PG_VERSION=9.3 \
    PG_USER=postgres \
    PG_HOME=/var/lib/postgresql \
    PG_RUNDIR=/run/postgresql \
    PG_LOGDIR=/var/log/postgresql

ENV PG_CONFDIR="/etc/postgresql/${PG_VERSION}/main" \
    PG_BINDIR="/usr/lib/postgresql/${PG_VERSION}/bin" \
    PG_DATADIR="${PG_HOME}/${PG_VERSION}/main"

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo 'deb http://apt.postgresql.org/pub/repos/apt/ wheezy-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql-${PG_VERSION} postgresql-client-${PG_VERSION} postgresql-contrib-${PG_VERSION} \
    && rm -rf ${PG_HOME} \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements/local.txt
RUN pip install -r requirements/test.txt

# Add repo contents to image
ADD . /app/

ENV PORT 8000
EXPOSE 8000
