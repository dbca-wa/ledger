[![Build
status](https://travis-ci.org/dbca-wa/ledger.svg?branch=master)](https://travis-ci.org/dbca-wa/ledger/builds) [![Coverage Status](https://coveralls.io/repos/github/dbca-wa/ledger/badge.svg?branch=master)](https://coveralls.io/github/dbca-wa/ledger?branch=master)
# Ledger

This project is the hub of the Department's online commerce activities.
It provides authentication, address and online payments functionality.

# Requirements

- Python (2.7.x)
- PostgreSQL (>=9.3)

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

