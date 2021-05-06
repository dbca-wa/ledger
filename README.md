[![Build
status](https://travis-ci.org/dbca-wa/ledger.svg?branch=master)](https://travis-ci.org/dbca-wa/ledger/builds) [![Coverage Status](https://coveralls.io/repos/github/dbca-wa/ledger/badge.svg?branch=master)](https://coveralls.io/github/dbca-wa/ledger?branch=master)
# Ledger

This project is the hub of the Department's online commerce activities.
It provides authentication, address and online payments functionality.

# Requirements

- Python (3.6.x)
- PostgreSQL (>=9.6)

Python library requirements should be installed using `pip`:

`pip install -r requirements.txt`

# Environment settings

A `.env` file should be created in the project root and used to set
required environment variables at run time. Example content:

    DEBUG=True
    DATABASE_URL="postgis://USER:PASSWORD@HOST:PORT/NAME"
    SECRET_KEY="ThisIsASecretKey"
    DEFAULT_HOST="https://website.domain/"
    EMAIL_HOST="emailhost"
    EMAIL_FROM="system@email.address"
    PARENT_HOST="website.domain"
    HOST_PORT=""
    ALLOWED_HOSTS=[u'website.domain']
    CMS_URL="https://url-used-to-retrieve-system-id-via-api/"
    LEDGER_USER="UserForSystemIdAPI"
    LEDGER_PASS="Password"
    BPOINT_BILLER_CODE="1234567"
    BPOINT_USERNAME="Username"
    BPOINT_PASSWORD="Password"
    BPOINT_MERCHANT_NUM="1234567889012345"
    BPAY_BILLER_CODE="123456"
    BPAY_FILE_PATH="/file/path/for/incoming/bpay/files"
    OSCAR_SHOP_NAME="Shop 1"
    NOTIFICATION_EMAIL="email@for.bpay.notifications"
    PRODUCTION_EMAIL=False (Send system emails to NON_PROD_EMAIL if False)
    EMAIL_INSTANCE='UAT' (DEV/TEST/UAT/PROD)
    NON_PROD_EMAIL='comma@separated.email,listfor@nonproduction.emails'


# Setting up a Ledger GW Server 

Version 1 of ledger gw will run in the same database,  however going forward Ledger GW will be seperated from other ledger apps with connection to ledger via API's. 

* Step 1: Clone this respository to your dev/uat/prod area.
* Step 2: Create a virtualenv for the ledgergw app "virtualenv -p python3 venv"  inside the cloned respository
* Step 3: activate environment source venv/bin/activate
* Step 4: Install requirements.  "pip install -r requirements.txt"
* Step 5: Setup .env file (link to same database as your app) 
* Step 6: python manage_ledgergw.py runserver 0.0.0.0:9010 (port can be set to your preference for development) otherwise another webserver such gunicorn can be used.
* Step 7: Access the django admin area on the port and ip.
* Step 8: Under django admin goto apis.
* Step 9: Click Add API and enter system name, api key will be automatically generated on save.  System ID optional. Allow IP's for developement should be 127.0.0.1/8 or for dev docker environments 172.17.0.0/8 or 172.10.0.0/8
