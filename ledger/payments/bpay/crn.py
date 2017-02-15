from py4j.java_gateway import JavaGateway, GatewayParameters

def  getCRN(number):
    gateway = JavaGateway()
    crn = gateway.entry_point.getCRN()
    return crn.generateBPAYCrnWithMod10V05(str(number))

def getICRN(number,amount,option='ICRNAMT'):
    gateway = JavaGateway()
    crn = gateway.entry_point.getiCRN()
    if option == 'ICRNAMT':
        return crn.generateBPAYIcrnAmt(str(number),str(amount))
    '''For later implementation
    elif option == 'ICRNAMTDTE':
        return generateBPAYIcrnAmtDate(number,amount,date)
    elif option == 'ICRNDATE':
        return generateBPAYIcrnDate(number,amount)
    '''