from py4j.java_gateway import JavaGateway, GatewayParameters
from py4j.protocol import Py4JNetworkError
from django.conf import settings
import re
from decimal import Decimal


gateway = JavaGateway(gateway_parameters=GatewayParameters(address=settings.BPAY_GATEWAY,port=25333,read_timeout=10))

def test_connection():
    try:
        gateway.jvm.System.currentTimeMillis()
    except Py4JNetworkError:
        raise Exception('Cannot connect to gateway server')
    except Exception as e:
        raise e
    finally:
        gateway.close()


def getCRN(number):
    if settings.BPAY_GATEWAY:
        test_connection()
        crn = gateway.entry_point.getCRN()
        return crn.generateBPAYCrnWithMod10V05(str(number))
    return generate_crn(number)


def getICRN(number,amount,option='ICRNAMT'):
    if settings.BPAY_GATEWAY:
        test_connection()
        crn = gateway.entry_point.getiCRN()
        if option == 'ICRNAMT':
            return crn.generateBPAYIcrnAmt(str(number),str(amount))
        '''For later implementation
        elif option == 'ICRNAMTDTE':
            return generateBPAYIcrnAmtDate(number,amount,date)
        elif option == 'ICRNDATE':
            return generateBPAYIcrnDate(number,amount)
        '''
    if option == 'ICRNAMT':
        return generate_icrnamt(number, amount)



def calc_check_digit(digits, weights, divide=10, subtract=0, add_digits=False, start_left=False):
    check = 0

    assert len(digits) <= 20

    def aggregate(content, reverse=False):
        total = 0
        for i in range(len(content)):
            ic, iw = (i, i) if (start_left ^ reverse) else (len(content)-i-1, len(weights)-i-1)
            sub = (ord(content[ic])-ord('0'))*weights[iw]
            if add_digits == 'Y':
                sub %= 100
                sub = (sub // 10) + (sub % 10)
            total += sub
        return total

    # from what I can tell, if a figure contains a decimal point:
    # - calculate normal check digit for the integral portion
    # - round the decimal portion of the price to 2 places
    # - for those two places, calculate the check digit while reading the figures/weights in reverse
    # - add and mod two check digits to get final

    if re.match('^[0-9]+\.[0-9]+$', digits):
        figure = round(Decimal(digits), 2)
        digits, dec = str(figure).split('.')
        check += aggregate(dec, reverse=True)
    else:
        assert re.match('^[0-9]+$', digits)

    check += aggregate(digits)
    check %= divide
    if subtract:
        check = (subtract - check) % divide
    return str(check)


def mod10v01(id_str):
    return calc_check_digit(id_str,
                            weights=[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                            subtract=10, add_digits='Y')

def mod10v05(id_str):
    return calc_check_digit(id_str,
                            weights=[1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,18,19,20],
                            start_left=True)

def mod10v05_r(id_str):
    return calc_check_digit(id_str,
                            weights=[1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,18,19,20])

def mod10v10(id_str):
    return calc_check_digit(id_str,
                            weights=[3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7],
                            subtract=10)

def generate_crn(id_str):
    assert 1 <= len(id_str) <= 20

    return '{0}{1}'.format(id_str, mod10v05(id_str))


def generate_icrnamt(id_str, amount_str):
    assert 1 <= len(id_str) <= 17

    result = '{0}{1}{2}'.format(mod10v01(amount_str), mod10v05_r(amount_str), id_str)
    return '{0}{1}'.format(result, mod10v10(result))

