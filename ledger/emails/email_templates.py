# email
from wagov_utils.components.utils.email import TemplateEmailBase as WAGovUtilsTemplateEmailBase

class DebtorReport(WAGovUtilsTemplateEmailBase):
    """Email Debtor Report."""
    subject = "Email Debtor Report"
    html_template = "email/base_email-oim.html"
    txt_template = "email/base_email-oim.txt"  