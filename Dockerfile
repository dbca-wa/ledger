# Dockerfile to build parkstay application images.
# Copy this file into the project root when building a new image.
# Prepare the base environment.
FROM python:3.7.2-slim-stretch as builder_base_parkstay
MAINTAINER asi@dbca.wa.gov.au
RUN apt-get update -y \
  && apt-get install --no-install-recommends -y wget git libmagic-dev gcc binutils libproj-dev gdal-bin python3-dev \
  && rm -rf /var/lib/apt/lists/*

# Install Python libs from requirements.txt.
FROM builder_base_parkstay as python_libs_parkstay
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_parkstay
COPY gunicorn.ini ./
COPY manage_ps.py ./manage.py
COPY ledger ./ledger
COPY parkstay ./parkstay
RUN python manage.py collectstatic --noinput
EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["gunicorn", "parkstay.wsgi", "--bind", ":8080", "--config", "gunicorn.ini"]
