from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import os
from datetime import datetime
from commercialoperator.utils.migration_utils import OrganisationReader, check_parks

import itertools

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Runs the initial deployment
    """

    help = 'Run the initial deployment'
    def handle(self, *args, **options):

        reader=OrganisationReader('/home/jawaidm/Downloads/Commercial-Licences-Migration-20191119 SH.csv')
        reader.create_organisation_data()

