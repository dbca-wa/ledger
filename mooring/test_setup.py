from django.test import TestCase
from django.test import Client
from mixer.backend.django import mixer

from ledger.accounts.models import EmailUser, EmailUserManager


class TestSetup(TestCase):
    client = Client()

    def setUp(self):
        instance = EmailUserManager()
        adminUser = EmailUser.objects.create_superuser(email="admin@website.domain", password="pass")
        user = EmailUser.objects.create_user(email="nonadmin@website.domain", password="pass")