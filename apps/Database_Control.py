import time
import numpy as np
import random
import math
import sqlite3
from CE import *

##########################################################################
def READ_Conf():
    conn=sqlite3.connect('rules.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM rules1 WHERE idd=?',[1])
    for row in cursor:
        ID = row[1]
        modulation = row[2]
        innercode = row[3]
        outercode = row[4]
    cursor.close()
    conn.close()
    Conf = make_Conf(ID,modulation,innercode,outercode)
    return Conf

##########################################################################
def WRITE_Conf(Conf,total,success,Throughput):
  try:
    connection = sqlite3.connect('config.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[Conf.ID])

    for row in cursor:
        trialN = row[4]
        TotalPacket = row[5]
        SUCCESSPacket = row[6]
        OLDThroughput = row[7]
        OLDSQTh = row[8]

    newTrialN = trialN + 1
    newTotal = TotalPacket + total
    newSuccess = SUCCESSPacket + success
    newThroughput = OLDThroughput + Throughput
    newSQTh = OLDSQTh + math.pow(Throughput,2)
    cursor.execute('UPDATE CONFIG SET TrialN=? ,TOTAL=? ,SUCCESS=? ,THROUGHPUT=? ,SQTh=? WHERE ID=?',[newTrialN,newTotal,newSuccess,newThroughput,newSQTh,Conf.ID])
    connection.commit()
    cursor.close()
    connection.close()
  except:
    cursor.close()
    connection.close()	
