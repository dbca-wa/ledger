from py4j.java_gateway import JavaGateway, GatewayParameters

def  getCRN(number):
    gateway = JavaGateway()
    crn = gateway.entry_point.getCRN()
    return crn.generateBPAYCrnWithMod10V01(str(number))

def getICRN(number,amount,date,option='ICRNAMT'):
    gateway = JavaGateway()
    crn = gateway.entry_point.getCRN()
    number = str(number)
    if option == 'ICRNDATE':
        return crn.generateBPAYIcrnDate(number,date)
    elif option == 'ICRNAMTDTE':
        return generateBPAYIcrnAmtDate(number,amount,date)
    elif option == 'ICRNAMT':
        return generateBPAYIcrnAmt(number,amount)
