from oscar.apps.payment.bankcards import *

CARD_TYPES = [
    (AMEX, (15,), ('34', '37')),
    (CHINA_UNIONPAY, (16, 17, 18, 19), ('62', '88')),
    (DINERS_CLUB, (14,), ('300', '301', '302', '303', '304', '305')),
    (DINERS_CLUB, (14,), ('36',)),
    (DISCOVER, (16,),
     list(map(str, list(range(622126, 622926)))) +
     list(map(str, list(range(644, 650)))) + ['6011', '65']),
    (JCB, (16,), map(str, list(range(3528, 3590)))),
    (LASER, list(range(16, 20)), ('6304', '6706', '6771', '6709')),
    (MAESTRO, list(range(12, 20)), ('5018', '5020', '5038', '5893', '6304',
                                    '6759', '6761', '6762', '6763', '0604')),
    (MASTERCARD, (16,), (list(map(str, list(range(2221, 2720)))) + list(map(str, list(range(51, 56)))))),
    # Diners Club cards match the same pattern as Mastercard.  They are treated
    # as Mastercard normally so we put the mastercard pattern first.
    (DINERS_CLUB, (16,), ('54', '55')),
    (SOLO, list(range(16, 20)), ('6334', '6767')),
    (SWITCH, list(range(16, 20)), ('4903', '4905', '4911', '4936',
                                   '564182', '633110', '6333', '6759')),
    (VISA, (13, 16), ('4',)),
    (VISA_ELECTRON, (16,), ('4026', '417500', '4405', '4508',
                            '4844', '4913', '4917')),
]