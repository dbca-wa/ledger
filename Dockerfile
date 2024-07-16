# Prepare the base environment.
FROM ubuntu:24.04 as builder_base_ledgergw
MAINTAINER asi@dbca.wa.gov.au
SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Australia/Perth
ENV PRODUCTION_EMAIL=True
ENV SECRET_KEY="ThisisNotRealKey"

# Use Australian Mirrors
RUN sed 's/archive.ubuntu.com/au.archive.ubuntu.com/g' /etc/apt/sources.list > /etc/apt/sourcesau.list
RUN mv /etc/apt/sourcesau.list /etc/apt/sources.list
# Use Australian Mirrors

RUN apt-get clean
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install --no-install-recommends -y wget git libmagic-dev gcc binutils libproj-dev gdal-bin python3 python3-setuptools python3-dev python3-pip tzdata cron
RUN apt-get install --no-install-recommends -y libpq-dev patch build-essential software-properties-common ca-certificates bzip2 gpg-agent 
RUN apt-get install --no-install-recommends -y npm bzip2 virtualenv
RUN update-ca-certificates
RUN apt-get install --no-install-recommends -y postgresql-client mtr htop vim ssh

RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install --no-install-recommends -y python3.7 python3.7-dev python3.7-distutils
# RUN ln -s /usr/bin/python3.7 /usr/bin/python && python3.7 -m pip install --upgrade pip==21.3.1
RUN apt-get update
RUN groupadd -g 5000 oim
RUN useradd -g 5000 -u 5000 oim -s /bin/bash -d /app
RUN usermod -a -G sudo oim
RUN mkdir /app
RUN chown -R oim.oim /app
# COPY cron /etc/cron.d/ledgergw
# RUN chmod 0644 /etc/cron.d/ledgergw
# RUN crontab /etc/cron.d/ledgergw
# RUN service cron start
# RUN touch /var/log/cron.log
# RUN service cron start

COPY timezone /etc/timezone
ENV TZ=Australia/Perth
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY startup.sh /
RUN chmod 755 /startup.sh

# kubernetes health checks script
RUN wget https://raw.githubusercontent.com/dbca-wa/wagov_utils/main/wagov_utils/bin/health_check.sh -O /bin/health_check.sh
RUN chmod 755 /bin/health_check.sh

# add python cron
RUN wget https://raw.githubusercontent.com/dbca-wa/wagov_utils/main/wagov_utils/bin-python/scheduler/scheduler.py -O /bin/scheduler.py
RUN chmod 755 /bin/scheduler.py


# Install Python libs from requirements.txt.
FROM builder_base_ledgergw as python_libs_ledgergw
WORKDIR /app
USER oim
RUN virtualenv -p python3.7 /app/venv
ENV PATH=/app/venv/bin:$PATH
COPY --chown=oim:oim requirements.txt ./
RUN whereis python
RUN python3.7 -V
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=oim:oim libgeos.py.patch /app/
RUN patch /app/venv/lib/python3.7/site-packages/django/contrib/gis/geos/libgeos.py /app/libgeos.py.patch
RUN rm /app/libgeos.py.patch

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_ledgergw
COPY --chown=oim:oim .git .git
COPY --chown=oim:oim python-cron python-cron
COPY gunicorn.ini manage_ledgergw.py ./
COPY ledger ./ledger
RUN find /app/

COPY --chown=oim:oim bin /app/bin
RUN find /app/bin
RUN touch /app/.env
COPY --chown=oim:oim ledgergw ./ledgergw
RUN chmod 755 /app/bin/*
RUN mkdir -p /app/ledgergw/cache/ 
RUN cd /app/ledgergw/static/common; npm install
# RUN cd /app/ledgergw/static/common; npm run build
RUN python manage_ledgergw.py collectstatic --noinput
# RUN service rsyslog start
USER root 
RUN  rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*
USER oim

EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/bin/bash", "-c", "/startup.sh"]
#CMD ["gunicorn", "ledgergw.wsgi", "--bind", ":8080", "--config", "gunicorn.ini"]
