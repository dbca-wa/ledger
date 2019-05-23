# Dockerfile to build parkstay application images.
# Copy this file into the project root when building a new image.
# Prepare the base environment.

FROM ubuntu:18.04 as builder_base_mooring
MAINTAINER asi@dbca.wa.gov.au
ENV DEBIAN_FRONTEND=noninteractive
ENV PRODUCTION_EMAIL=False
ENV NON_PROD_EMAIL='asi@dbca.wa.gov.au'
ENV EMAIL_INSTANCE='DEV'
ARG SECRET_KEY
ENV SECRET_KEY=$SECRET_KEY

#RUN apt-get update -y \
#  && apt-get install --no-install-recommends -y wget git libmagic-dev gcc binutils libproj-dev gdal-bin libpq-dev gunicorn\
#  python python-setuptools python-dev python-pip \
#  && pip install --upgrade pip

RUN apt-get update -y \ 
  && apt-get install --no-install-recommends -y wget git libmagic-dev gcc binutils libproj-dev gdal-bin libpq-dev gunicorn\
  python python-setuptools python-dev python-pip \
  && pip install --upgrade pip



# Install Python libs from requirements.txt.
FROM builder_base_mooring as python_libs_mooring
WORKDIR /app
RUN touch .env
# Used to purge browser cache
COPY .git/refs/heads/master /app/git_hash

# --no-cache-dir
COPY requirements.txt ./
RUN pip install -r requirements.txt \
  # Update the Django <1.11 bug in django/contrib/gis/geos/libgeos.py
  # Reference: https://stackoverflow.com/questions/18643998/geodjango-geosexception-error
  && sed -i -e "s/ver = geos_version().decode()/ver = geos_version().decode().split(' ')[0]/" /usr/local/lib/python2.7/dist-packages/django/contrib/gis/geos/libgeos.py \
  && rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_mooring
COPY gunicorn.ini ./
COPY manage_mo.py ./manage_mo.py
COPY ledger ./ledger
COPY mooring ./mooring
RUN python manage_mo.py collectstatic --noinput
EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["gunicorn", "mooring.wsgi", "--bind", ":8080", "--config", "gunicorn.ini"]
