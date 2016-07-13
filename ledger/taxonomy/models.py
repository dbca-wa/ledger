import os
import json
import logging
import requests

from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)


class SpeciesManager(models.Manager):
    """Create a custom Manager to allow searching on similarity of species
    names, for validation purposes.
    """

    def update_herbie_hbvspecies(self):
        """Query data from the HERBIE WFS, served via KMI.
        """
        source = 'herbie'
        logger.info('Querying HERBIE.HBVSPECIES for species names')
        url = settings.KMI_WFS_URL
        r = requests.post(url)
        if r.status_code != 200:
            r.raise_for_status()

        j = json.loads(r.content)
        total = len(j['features'])

        logger.info('Updating local cache of {} species names from HERBIE.HBVSPECIES'.format(total))

        # We don't do update! Delete all 'herbie' species currently stored
        self.filter(source=source).delete()
        # Load each of the species.
        objects = []
        for i in j['features']:
            properties = i['properties']
            fields = {
                'species_name': properties['species_name'],
                'name_id': properties['name_id'],
                'consv_code': properties['consv_code'],
                'source': source
            }
            species = Species(**fields)
            objects.append(species)
        # bulk create
        self.bulk_create(objects)
        logger.info('Completed ({} new species created).'.format(len(objects)))

    def similar_name(self, species_name, similarity=0.4):
        """Returns a RawQuerySet object.
        """
        return self.raw("""SELECT id, species_name, similarity(species_name, '{0}') AS sml
            FROM taxonomy_species
            WHERE species_name %% '{0}'
            AND similarity(species_name, '{0}') > {1}
            ORDER BY sml DESC, species_name
            """.format(species_name, similarity))


class Species(models.Model):
    """Species names are saved for validation purposes.
    Data is sourced externally, and not intended to be edited within Biosys.
    This is basically a cached version of the herbie database.
    To update:  see SpeciesManager update_herbie_hbvspecies method
    """
    name_id = models.IntegerField(blank=False,
                                  verbose_name="Name ID", help_text="Unique species reference")
    species_name = models.CharField(max_length=256, db_index=True)
    consv_code = models.CharField(max_length=10, null=True, blank=True,
                                  verbose_name="Conservation status", help_text="")
    source = models.CharField(max_length=64, db_index=True)
    objects = SpeciesManager()

    class Meta:
        ordering = ['species_name']
        verbose_name_plural = 'species'

    def __unicode__(self):
        return self.species_name


class SpeciesFile(models.Model):
    validated = models.BooleanField(default=False, verbose_name="Validated",
                                    help_text="True if every species name in the file has been validated against Herbie")
    comments = models.TextField(blank=True,
                                verbose_name="Comments", help_text="")

    file = models.FileField(upload_to='%Y/%m/%d')
    uploaded_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.file.name

    @property
    def path(self):
        return self.file.path

    @property
    def filename(self):
        return os.path.basename(self.path)
