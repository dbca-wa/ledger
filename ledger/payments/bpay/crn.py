from py4j.java_gateway import JavaGateway, GatewayParameters
from py4j.protocol import Py4JNetworkError
from django.conf import settings

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
    test_connection()
    crn = gateway.entry_point.getCRN()
    return crn.generateBPAYCrnWithMod10V05(str(number))

def getICRN(number,amount,option='ICRNAMT'):
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
