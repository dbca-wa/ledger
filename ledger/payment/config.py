from oscar.apps.payment import config


class PaymentConfig(config.PaymentConfig):
    name = 'ledger.payment'
