import time
import numpy as np
import random
import math
import sqlite3
import sys
from CE import *


class DatabaseControl:
    def __init__(self):
        self.config_connection = sqlite3.connect('config.db')
        self.config_cursor = self.config_connection.cursor()
        self.rules_connection = sqlite3.connect('rules.db')
        self.rules_cursor = self.rules_connection.cursor()

    def __del__(self):
        self.config_connection.close()
        self.rules_connection.close()

    ##########################################################################
    def read_configuration(self):
        self.rules_cursor.execute('SELECT * FROM rules1 WHERE idd=?', [1])
        for row in self.rules_cursor:
            ID = row[1]
            modulation = row[2]
            innercode = row[3]
            outercode = row[4]
        Conf = make_Conf(ID, modulation, innercode, outercode)
        return Conf

    ##########################################################################
    def write_configuration(self, Conf, total, success, Throughput):
        try:
            self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [Conf.ID])
            for row in self.config_cursor:
                trialN = row[4]
                TotalPacket = row[5]
                SUCCESSPacket = row[6]
                OLDThroughput = row[7]
                OLDSQTh = row[8]

            newTrialN = trialN + 1
            newTotal = TotalPacket + total
            newSuccess = SUCCESSPacket + success
            newThroughput = OLDThroughput + Throughput
            newSQTh = OLDSQTh + math.pow(Throughput, 2)
            self.config_cursor.execute('UPDATE CONFIG SET TrialN=? ,TOTAL=? ,SUCCESS=? ,THROUGHPUT=? ,SQTh=? WHERE ID=?',
                           [newTrialN, newTotal, newSuccess, newThroughput, newSQTh, Conf.ID])
            self.config_connection.commit()
        except Exception as e:
            print e

        # except sqlite3.ProgrammingError as e:
        #     print sys.exc_info()[0]
        #     pass


