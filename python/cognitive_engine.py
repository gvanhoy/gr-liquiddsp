#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2017 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr
import sqlite3
import pmt
import sys
import numpy as np


class cognitive_engine(gr.sync_block):
    """
    docstring for block cognitive_engine
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name="cognitive_engine",
            in_sig=[],
            out_sig=[])
        self.database = DatabaseControl()
        self.database.create_tables()
        self.database.reset_tables()
        self.engine = CognitiveEngine()
        self.message_port_register_in(pmt.intern('packet_info'))
        self.set_msg_handler(pmt.intern('packet_info'), self.handler)
        self.message_port_register_out(pmt.intern('configuration'))
        self.num_packets = 0

    def handler(self, packet_info):
        self.num_packets += 1
        modulation = pmt.to_python(pmt.dict_ref(packet_info, pmt.intern("modulation"), pmt.PMT_NIL))
        inner_code = pmt.to_python(pmt.dict_ref(packet_info, pmt.intern("inner_code"), pmt.PMT_NIL))
        outer_code = pmt.to_python(pmt.dict_ref(packet_info, pmt.intern("outer_code"), pmt.PMT_NIL))
        payload_valid = pmt.to_python(pmt.dict_ref(packet_info, pmt.intern("header_valid"), pmt.PMT_NIL))
        header_valid = pmt.to_python(pmt.dict_ref(packet_info, pmt.intern("payload_valid"), pmt.PMT_NIL))
        config_id = modulation*11 + inner_code*7 + outer_code + 1
        configuration = ConfigurationMap(modulation, inner_code, outer_code, config_id)
        goodput = np.log2(configuration.constellationN) * (float(configuration.outercodingrate)) * (float(configuration.innercodingrate)) * payload_valid
        self.database.write_configuration(configuration,
                                          payload_valid,
                                          header_valid,
                                          goodput)

        ce_configuration = self.engine.epsilon_greedy(.01)
        if ce_configuration is not None:
            new_configuration = pmt.make_dict()
            new_ce_configuration = ce_configuration[0]
            new_configuration = pmt.dict_add(new_configuration, pmt.intern("modulation"), pmt.from_long(new_ce_configuration.modulation))
            new_configuration = pmt.dict_add(new_configuration, pmt.intern("inner_code"), pmt.from_long(new_ce_configuration.innercode))
            new_configuration = pmt.dict_add(new_configuration, pmt.intern("outer_code"), pmt.from_long(new_ce_configuration.outercode))
            self.message_port_pub(pmt.intern('configuration'), new_configuration)


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
    # def read_configuration(self):
    #     self.rules_cursor.execute('SELECT * FROM rules1 WHERE idd=?', [1])
    #     for row in self.rules_cursor:
    #         ID = row[1]
    #         modulation = row[2]
    #         innercode = row[3]
    #         outercode = row[4]
    #     Conf = ConfigurationMap(ID, modulation, innercode, outercode)
    #     return Conf

    ##########################################################################
    def write_configuration(self, configuration, total, success, throughput):
        try:
            self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [configuration.conf_id])
            for row in self.config_cursor:
                num_trial = row[4]
                total_packet = row[5]
                success_packet = row[6]
                old_throughput = row[7]
                old_sqth = row[8]

            newTrialN = num_trial + 1
            newTotal = total_packet + total
            newSuccess = success_packet + success
            newThroughput = old_throughput + throughput
            newSQTh = old_sqth + np.pow(throughput, 2)
            self.config_cursor.execute('UPDATE CONFIG SET TrialN=? ,TOTAL=? ,SUCCESS=? ,THROUGHPUT=? ,SQTh=? WHERE ID=?',
                           [newTrialN, newTotal, newSuccess, newThroughput, newSQTh, Conf.ID])
            self.config_connection.commit()
        except Exception as e:
            print e

    def reset_tables(self):
        connection = self.config_connection
        cursor = self.config_cursor
        cursor.execute('SELECT MAX(ID) FROM CONFIG')
        Allconfigs = cursor.fetchone()[0]

        # Egreedy
        for i in xrange(1, Allconfigs + 1):
            cursor.execute('UPDATE CONFIG SET TrialN=? ,TOTAL=? ,SUCCESS=? ,THROUGHPUT=? ,SQTh=? WHERE ID=?',
                           [0, 0, 0, 0.0, 0.0, i])
        connection.commit()

        cursor.execute('drop table if exists Egreedy')
        connection.commit()

        sql = 'create table if not exists Egreedy (ID integer primary key, TrialNumber integer default 0, Mean integer default 0, Lower real default 0.0, Upper real default 0.0, Eligibility int default 1)'
        cursor.execute(sql)
        for j in xrange(1, Allconfigs + 1):
            cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [j])
            for row in cursor:
                Modulation = row[1]
                InnerCode = row[2]
                OuterCode = row[3]
            config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
            upperbound = np.log2(config_map.constellationN) * (float(config_map.outercodingrate)) * (
            float(config_map.innercodingrate))
            cursor.execute('INSERT INTO Egreedy (ID,TrialNumber,Mean,Lower,Upper,Eligibility) VALUES (?,?,?,?,?,?)',
                           (j, 0, 0, 0, upperbound, 1))
        connection.commit()

        # Boltmann
        cursor.execute('drop table if exists Boltzmann')
        connection.commit()

        sql = 'create table if not exists Boltzmann (ID integer primary key, TrialNumber integer default 0, Mean real default 0.0, Prob float default 1.0, Lower real default 0.0, Upper real default 0.0, Eligibility int default 1)'
        cursor.execute(sql)
        for j in xrange(1, Allconfigs + 1):
            cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [j])
            for row in cursor:
                Modulation = row[1]
                InnerCode = row[2]
                OuterCode = row[3]
                config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
            upperbound = np.log2(config_map.constellationN) * (float(config_map.outercodingrate)) * (
            float(config_map.innercodingrate))
            cursor.execute(
                'INSERT INTO Boltzmann (ID,TrialNumber,Mean,Prob,Lower,Upper,Eligibility) VALUES (?,?,?,?,?,?,?)',
                (j, 0, 0, 1.0, 0, upperbound, 1))

        # Gittins
        connection.commit()
        cursor.execute('drop table if exists Gittins')
        connection.commit()
        sql = 'create table if not exists Gittins (ID integer primary key, TrialNumber integer default 0, Mean real default 0.0, Stdv real default 1.0, Indexx float default 0)'
        cursor.execute(sql)
        for j in xrange(1, Allconfigs + 1):
            cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [j])
            for row in cursor:
                Modulation = row[1]
                InnerCode = row[2]
                OuterCode = row[3]
                config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
            upperbound = np.log2(config_map.constellationN) * (float(config_map.outercodingrate)) * (
            float(config_map.innercodingrate))
            cursor.execute('INSERT INTO Gittins (ID,TrialNumber,Mean,Stdv,Indexx) VALUES (?,?,?,?,?)',
                           (j, 0, 0.0, 0.0, upperbound))

        connection.commit()

        # UCB
        cursor.execute('drop table if exists UCB')
        connection.commit()
        sql = 'create table if not exists UCB (ID integer primary key, TrialNumber integer default 0, Mean real default 0.0, Ind float default 0)'
        cursor.execute(sql)
        M = 64
        maxReward = np.log2(M)
        for j in xrange(1, Allconfigs + 1):
            cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [j])
            for row in cursor:
                Modulation = row[1]
                InnerCode = row[2]
                OuterCode = row[3]
                config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
            upperbound = np.log2(config_map.constellationN) * (float(config_map.outercodingrate)) * (
            float(config_map.innercodingrate))
            Mean = upperbound / maxReward
            bonus = np.sqrt(2 * np.log10(Allconfigs))
            ind = Mean + bonus
            cursor.execute('INSERT INTO UCB (ID,TrialNumber,Mean,Ind) VALUES (?,?,?,?)', (j, 1, Mean, ind))

        connection.commit()
        cursor.close()
        connection.close()

    def create_tables(self):
        ######################################################################
        self.config_connection.execute('''drop table if exists config;''')
        self.config_connection.execute(
            '''CREATE TABLE if not exists CONFIG
            (ID INT PRIMARY KEY         NOT NULL,
            MODULATION       INT        NOT NULL,
            Innercode        INT        NOT NULL,
            Outercode        INT        NOT NULL,
            TrialN           INT        NOT NULL,
            Total            INT        NOT NULL,
            Success          INT        NOT NULL,
            Throughput       REAL       NOT NULL,
            SQTh             REAL       NOT NULL);''')
        print "Table created successfully"
        conf_id = 0
        for m in xrange(0, 11):
            for i in xrange(0, 7):
                for o in xrange(0, 8):
                    self.config_connection.execute('INSERT INTO CONFIG (ID,MODULATION,Innercode,Outercode,TrialN,Total,Success,Throughput,SQTh) \
                              VALUES (?, ?, ?, ?, 0, 0, 0, 0.0, 0.0)', (conf_id, m, i, o))
                    conf_id += 1
        self.config_connection.commit()

        print "Config Records created successfully"
        #################################################################################################################################

        self.rules_connection.execute('''drop table if exists rules1;''')
        self.rules_connection.execute(
            '''CREATE TABLE if not exists rules1
            (idd  INT PRIMARY KEY       NOT NULL,
            ID               INT        NOT NULL,
            MODULATION       INT        NOT NULL,
            Innercode        INT        NOT NULL,
            Outercode        INT        NOT NULL);''')
        print "rules Table created successfully"
        self.rules_connection.execute('INSERT INTO rules1 (idd,ID,MODULATION,Innercode,Outercode) \
              VALUES (1,1, 0, 0, 0)')
        self.rules_connection.execute('INSERT INTO rules1 (idd,ID,MODULATION,Innercode,Outercode) \
              VALUES (2,2, 0, 0, 0)')
        self.rules_connection.commit()
        print "rules1 Records created successfully"


class ConfigurationMap:
    def __init__(self, modulation, inner_code, outer_code, conf_id=0):
        self.id = conf_id
        self.constellationN = 0
        self.modulationtype = ""
        self.innercodingrate = 0
        self.innercodingtype = ""
        self.outercodingrate = 0
        self.outercodingtype = ""
        self.set_configuration(modulation, inner_code, outer_code)

    def set_configuration(self, modulation, inner_code, outer_code):
        if modulation == 0:
            self.constellationN = 2
            self.modulationtype = 'PSK'
        elif modulation == 1:
            self.constellationN = 4
            self.modulationtype = 'PSK'
        elif modulation == 2:
            self.constellationN = 8
            self.modulationtype = 'PSK'
        elif modulation == 3:
            self.constellationN = 16
            self.modulationtype = 'PSK'
        elif modulation == 4:
            self.constellationN = 2
            self.modulationtype = 'DPSK'
        elif modulation == 5:
            self.constellationN = 4
            self.modulationtype = 'DPSK'
        elif modulation == 6:
            self.constellationN = 8
            self.modulationtype = 'DPSK'
        elif modulation == 7:
            self.constellationN = 4
            self.modulationtype = 'ASK'
        elif modulation == 8:
            self.constellationN = 16
            self.modulationtype = 'QAM'
        elif modulation == 9:
            self.constellationN = 32
            self.modulationtype = 'QAM'
        elif modulation == 10:
            self.constellationN = 64
            self.modulationtype = 'QAM'

        if inner_code == 0:
            self.innercodingrate = float(1)
            self.innercodingtype = 'None'
        elif inner_code == 1:
            self.innercodingrate = float(1) / float(2)
            self.innercodingtype = 'Conv'
        elif inner_code == 2:
            self.innercodingrate = float(2) / float(3)
            self.innercodingtype = 'Conv'
        elif inner_code == 3:
            self.innercodingrate = float(3) / float(4)
            self.innercodingtype = 'Conv'
        elif inner_code == 4:
            self.innercodingrate = float(4) / float(5)
            self.innercodingtype = 'Conv'
        elif inner_code == 5:
            self.innercodingrate = float(5) / float(6)
            self.innercodingtype = 'Conv'
        elif inner_code == 6:
            self.innercodingrate = float(6) / float(7)
            self.innercodingtype = 'Conv'

        if outer_code == 0:
            self.outercodingrate = float(1)
            self.outercodingtype = 'None'
        elif outer_code == 1:
            self.outercodingrate = float(12) / float(24)
            self.outercodingtype = 'Golay'
        elif outer_code == 2:
            self.outercodingrate = float(4) / float(8)
            self.outercodingtype = 'Reed-Solomon'
        elif outer_code == 3:
            self.outercodingrate = float(4) / float(7)
            self.outercodingtype = 'Hamming'
        elif outer_code == 4:
            self.outercodingrate = float(8) / float(12)
            self.outercodingtype = 'Hamming'
        elif outer_code == 5:
            self.outercodingrate = float(16) / float(22)
            self.outercodingtype = 'SECDED'
        elif outer_code == 6:
            self.outercodingrate = float(32) / float(39)
            self.outercodingtype = 'SECDED'
        elif outer_code == 7:
            self.outercodingrate = float(64) / float(72)
            self.outercodingtype = 'SECDED'


class CognitiveEngine:
    def __init__(self):
        pass

    def epsilon_greedy(self, epsilon):
        try:
            connection = sqlite3.connect('config.db')
            cursor = connection.cursor()
            cursor.execute('SELECT MAX(ID) FROM CONFIG')
            Allconfigs = cursor.fetchone()[0]

            for j in xrange(1, Allconfigs + 1):
                cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [j])
                for row in cursor:
                    Modulation = row[1]
                    InnerCode = row[2]
                    OuterCode = row[3]
                    trialN = row[4]
                    total = row[5]
                    success = row[6]
                    throughput = row[7]
                    sqth = row[8]
                if trialN > 0:
                    mean = throughput / trialN
                    variance = (sqth / trialN) - (np.pow(mean, 2))
                    if variance < 0:
                        variance = 0
                    config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
                    maxp = np.log2(config_map.constellationN) * (float(config_map.outercodingrate)) * (
                    float(config_map.innercodingrate))
                    unsuccess = total - success
                    PSR = float(success) / total
                    cursor.execute('UPDATE Egreedy set TrialNumber=? ,Mean=? WHERE ID=?', [trialN, mean, j])
                if trialN > 1:
                    RCI = self.CI(mean, variance, maxp, confidence, trialN)
                    lower = RCI[0]
                    upper = RCI[1]
                    cursor.execute('UPDATE Egreedy set TrialNumber=? ,Mean=? ,Lower=? ,Upper=? WHERE ID=?',
                                   [trialN, mean, lower, upper, j])
            connection.commit()

            cursor.execute('SELECT MAX(Mean) FROM Egreedy')
            muBest = cursor.fetchone()[0]
            print "muBest = ", muBest
            for j in xrange(1, Allconfigs + 1):
                cursor.execute('SELECT Upper FROM Egreedy WHERE ID=?', [j])
                upper = cursor.fetchone()[0]
                if upper < muBest:
                    # FAST FIX! change 0 for quick fix to 1, makes all methods eligable
                    cursor.execute('UPDATE Egreedy set Eligibility=? WHERE ID=?', [0, j])
                else:
                    cursor.execute('UPDATE Egreedy set Eligibility=? WHERE ID=?', [1, j])
            connection.commit()

            cursor.execute('SELECT count(*) FROM Egreedy WHERE Mean=?', [muBest])
            NO = cursor.fetchone()[0]
            nn = random.randrange(1, NO + 1)
            cursor.execute('SELECT ID FROM Egreedy WHERE Mean=?', [muBest])
            j = 0
            for row in cursor:
                j = j + 1
                if j == nn:
                    configN = row[0]
                    cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [configN])
                    for row1 in cursor:
                        NextConf2 = ConfigurationMap(row1[1], row1[2], row1[3], row1[0])
                        print "Configuration is"
                        config_map = ConfigurationMap(NextConf2.modulation, NextConf2.innercode, NextConf2.outercode)
                        print "Modulation is ", config_map.constellationN, config_map.modulationtype
                        print "Inner Code is ", config_map.innercodingtype, ", and coding rate is ", config_map.innercodingrate
                        print "Outer Code is ", config_map.outercodingtype, ", and coding rate is ", config_map.outercodingrate
                        print "###############################\n\n"
                    break

            if random.random() > epsilon:
                print "***Exploitation***\n"
                NextConf1 = NextConf2

            else:
                print "***Exploration***\n"
                cursor.execute('SELECT count(*) FROM Egreedy')
                NO = cursor.fetchone()[0]
                nn = random.randrange(1, NO + 1)
                cursor.execute('SELECT ID FROM Egreedy')
                j = 0
                for row in cursor:
                    j = j + 1
                    if j == nn:
                        configN = row[0]
                        break

                cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [configN])
                for row in cursor:
                    NextConf1 = ConfigurationMap(row[1], row[2], row[3], row[0])
                    print "Configuration is"
                    config_map = ConfigurationMap(NextConf1.modulation, NextConf1.innercode, NextConf1.outercode)
                    print "Modulation is ", config_map.constellationN, config_map.modulationtype
                    print "Inner Code is ", config_map.innercodingtype, ", and coding rate is ", config_map.innercodingrate
                    print "Outer Code is ", config_map.outercodingtype, ", and coding rate is ", config_map.outercodingrate
                    print "###############################\n\n"

            cursor.close()
            connection.close()
            return NextConf1, NextConf2
        except:
            print "Error with database.", sys.exc_info()[0]
            cursor.close()
            connection.close()

    def CI(self, mean, variance, maxp, confidence, N):
        C = 1 - ((1 - confidence) / 2)
        std = np.sqrt(variance)
        coefficient = t.ppf(C, N - 1)
        RCIl = mean - (coefficient * (std / np.sqrt(N)))
        if RCIl < 0:
            RCIl = 0

        RCIu = mean + (coefficient * (std / np.sqrt(N)))
        if RCIu > maxp:
            RCIu = maxp

        RCI = [RCIl, RCIu]
        return RCI
