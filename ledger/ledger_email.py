import smtplib

from django.conf import settings
from django.core.mail.message import sanitize_address
from django.core.mail.backends.smtp import EmailBackend

class LedgerEmailBackend(EmailBackend):
    
    def _send(self, email_message):
        """A helper method that does the actual sending"""
        if not email_message.recipients():
            return False
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        if not settings.PRODUCTION_EMAIL:
            recipients = settings.NON_PROD_EMAIL.split(',')
            email_message.subject = '{} {}'.format(email_message.subject, settings.EMAIL_INSTANCE)
        else:
            recipients = [sanitize_address(addr, encoding) for addr in email_message.recipients()]
        message = email_message.message()
        
        try:
            self.connection.sendmail(from_email, recipients, message.as_bytes(linesep='\r\n'))
        except smtplib.SMTPException:
            if not self.fail_silently:
                raise
            return False
        return True
    

