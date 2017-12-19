from django.test import TestCase

from wildlifelicensing.apps.emails.emails import TemplateEmailBase, MAX_SUBJECT_LENGTH
from wildlifelicensing.apps.main.tests import helpers


class EmailTest(TestCase):

    def setUp(self):
        helpers.clear_mailbox()

    def test_subject_max_length(self):
        """Test that a long subject is shorten"""
        email = TemplateEmailBase()
        subject = 'A verrrrrrrryyyyyyyyyyyyyyyyyy loooooooooooooooooooooooooooooooooooooooong subbbbbbbbbjjjjjjjjjjeeeeeect'
        email.subject = subject
        self.assertTrue(len(subject) > MAX_SUBJECT_LENGTH)
        self.assertFalse(helpers.is_email())
        email.send(['recipient@test.com'])
        emails = helpers.get_emails()
        self.assertEqual(len(emails), 1)
        email = emails[0]
        self.assertEqual(len(email.subject), MAX_SUBJECT_LENGTH)
        expected_subject = '{}..'.format(subject[:MAX_SUBJECT_LENGTH - 2])
        self.assertEqual(email.subject, expected_subject)
