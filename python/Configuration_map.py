class Config_map (object):
    constellationN=0
    modulationtype=""
    innercodingrate=0
    innercodingtype=""
    outercodingrate=0
    outercodingtype=""

    def __init__(self,constellationN,modulationtype,innercodingrate,innercodingtype,outercodingrate,outercodingtype):
        self.constellationN=constellationN
        self.modulationtype=modulationtype
        self.innercodingrate=innercodingrate
        self.innercodingtype=innercodingtype
        self.outercodingrate=outercodingrate
        self.outercodingtype=outercodingtype


def make_Config_map(constellationN,modulationtype,innercodingrate,innercodingtype,outercodingrate,outercodingtype):
    Confiuration_map=Config_map(constellationN,modulationtype,innercodingrate,innercodingtype,outercodingrate,outercodingtype)
    return Confiuration_map   
    

def Conf_map(modulation, innercode, outercode):
    if modulation == 0:
        constellationN=2
        modulationtype='PSK'
    elif modulation == 1:
        constellationN=4
        modulationtype='PSK'
    elif modulation == 2:
        constellationN=8
        modulationtype='PSK'
    elif modulation == 3:
        constellationN=16
        modulationtype='PSK'
    elif modulation == 4:
        constellationN=2
        modulationtype='DPSK'
    elif modulation == 5:
        constellationN=4
        modulationtype='DPSK'
    elif modulation == 6:
        constellationN=8
        modulationtype='DPSK'
    elif modulation == 7:
        constellationN=4
        modulationtype='ASK'
    elif modulation == 8:
        constellationN=16
        modulationtype='QAM'
    elif modulation == 9:
        constellationN=32
        modulationtype='QAM'
    elif modulation == 10:
        constellationN=64
        modulationtype='QAM'

    if innercode == 0:
        innercodingrate=float(1)
        innercodingtype='None'
    elif innercode == 1:
        innercodingrate=float(1)/float(2)
        innercodingtype='Conv'
    elif innercode == 2:
        innercodingrate=float(2)/float(3)
        innercodingtype='Conv'
    elif innercode == 3:
        innercodingrate=float(3)/float(4)
        innercodingtype='Conv'
    elif innercode == 4:
        innercodingrate=float(4)/float(5)
        innercodingtype='Conv'
    elif innercode == 5:
        innercodingrate=float(5)/float(6)
        innercodingtype='Conv'
    elif innercode == 6:
        innercodingrate=float(6)/float(7)
        innercodingtype='Conv'

    if outercode == 0:
        outercodingrate=float(1)
        outercodingtype='None'
    elif outercode == 1:
        outercodingrate=float(12)/float(24)
        outercodingtype='Golay'
    elif outercode == 2:
        outercodingrate=float(4)/float(8)
        outercodingtype='Reed-Solomon'
    elif outercode == 3:
        outercodingrate=float(4)/float(7)
        outercodingtype='Hamming'
    elif outercode == 4:
        outercodingrate=float(8)/float(12)
        outercodingtype='Hamming'
    elif outercode == 5:
        outercodingrate=float(16)/float(22)
        outercodingtype='SECDED'
    elif outercode == 6:
        outercodingrate=float(32)/float(39)
        outercodingtype='SECDED'
    elif outercode == 7:
        outercodingrate=float(64)/float(72)
        outercodingtype='SECDED'

    C_map = make_Config_map(constellationN,modulationtype,innercodingrate,innercodingtype,outercodingrate,outercodingtype)

    return C_map

