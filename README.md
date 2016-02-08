[![Stories in Ready](https://badge.waffle.io/parksandwildlife/ledger.png?label=ready&title=Ready)](https://waffle.io/parksandwildlife/ledger)
# Ledger

This project is the hub of the Department's online commerce activities.
It provides CRM and online payments functionality.

# Requirements

- Python (2.7.x)
- PostgreSQL (>=9.3)

Python library requirements should be installed using `pip`:

`pip install -r requirements.txt`

# Environment settings

A `.env` file should be created in the project root and used to set
required environment variables at run time. Example content:

    DEBUG=True
    DATABASE_URL="postgres://USER:PASSWORD@HOST:PORT/NAME"
    SECRET_KEY="ThisIsASecretKey"
