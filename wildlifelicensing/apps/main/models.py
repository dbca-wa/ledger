from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Document(models.Model):
    name = models.CharField(max_length=100, blank=True,
                            verbose_name='name', help_text='')
    description = models.TextField(blank=True,
                                   verbose_name='description', help_text='')
    file = models.FileField(upload_to='%Y/%m/%d')
    uploaded_date = models.DateTimeField(auto_now_add=True)

    @property
    def path(self):
        return self.file.path

    @property
    def filename(self):
        return self.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename

    class Meta:
        db_table = 'wl_main_document'
