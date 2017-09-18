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
from scipy.stats import *
import numpy as np
import random

CONFIDENCE = 0.9
PSR_Threshold = 0.8


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
        self.database.reset_config_tables()
        self.database.reset_cognitive_engine_tables()
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
        header_valid = pmt.to_python(pmt.dict_ref(packet_info, pmt.intern("header_valid"), pmt.PMT_NIL))
        payload_valid = pmt.to_python(pmt.dict_ref(packet_info, pmt.intern("payload_valid"), pmt.PMT_NIL))
        config_id = modulation*7*8 + inner_code*8 + outer_code + 1
        configuration = ConfigurationMap(modulation, inner_code, outer_code, config_id)
        goodput = np.log2(configuration.constellationN) * (float(configuration.outercodingrate)) * (float(configuration.innercodingrate)) * payload_valid
        self.database.write_configuration(configuration,
                                          header_valid,
                                          payload_valid,
                                          goodput)

        ce_configuration = self.engine.epsilon_greedy(self.num_packets, .1)
        if ce_configuration is not None:
            new_configuration = pmt.make_dict()
            new_ce_configuration = ce_configuration[0]
            new_configuration = pmt.dict_add(new_configuration, pmt.intern("modulation"), pmt.from_long(new_ce_configuration.modulation))
            new_configuration = pmt.dict_add(new_configuration, pmt.intern("inner_code"), pmt.from_long(new_ce_configuration.inner_code))
            new_configuration = pmt.dict_add(new_configuration, pmt.intern("outer_code"), pmt.from_long(new_ce_configuration.outer_code))
            self.message_port_pub(pmt.intern('configuration'), new_configuration)


class DatabaseControl:
    def __init__(self):
        self.config_connection = sqlite3.connect('config.db', check_same_thread=False)
        self.config_cursor = self.config_connection.cursor()
        self.rules_connection = sqlite3.connect('rules.db', check_same_thread=False)
        self.rules_cursor = self.rules_connection.cursor()

    def __del__(self):
        self.config_connection.close()
        self.rules_connection.close()

    def write_configuration(self, configuration, total, success, throughput):
        self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [configuration.conf_id])
        has_row = False
        for row in self.config_cursor:
            num_trial = row[4]
            total_packet = row[5]
            success_packet = row[6]
            old_throughput = row[7]
            old_sqth = row[8]
            has_row = True

        if has_row:
            newTrialN = num_trial + 1
            newTotal = total_packet + total
            newSuccess = success_packet + success
            # newThroughput = old_throughput + throughput
            newThroughput = throughput
            newSQTh = old_sqth + np.power(throughput, 2)
            self.config_cursor.execute('UPDATE CONFIG SET TrialN=? ,TOTAL=? ,SUCCESS=? ,THROUGHPUT=? ,SQTh=? WHERE ID=?',
                           [newTrialN, newTotal, newSuccess, newThroughput, newSQTh, configuration.conf_id])
            self.config_connection.commit()

    def reset_cognitive_engine_tables(self):
        self.config_cursor.execute('SELECT MAX(ID) FROM CONFIG')
        Allconfigs = self.config_cursor.fetchone()[0]

        for i in xrange(1, Allconfigs + 1):
            self.config_cursor.execute('UPDATE CONFIG SET TrialN=? ,TOTAL=? ,SUCCESS=? ,THROUGHPUT=? ,SQTh=? WHERE ID=?',
                           [0, 0, 0, 0.0, 0.0, i])
        self.config_connection.commit()

        # Egreedy
        self.config_cursor.execute('drop table if exists Egreedy')
        self.config_connection.commit()

        sql = 'create table if not exists Egreedy (ID integer primary key, TrialNumber integer default 0, Mean integer default 0, Lower real default 0.0, Upper real default 0.0, Eligibility int default 1)'
        self.config_cursor.execute(sql)
        for j in xrange(1, Allconfigs + 1):
            self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [j])
            for row in self.config_cursor:
                Modulation = row[1]
                InnerCode = row[2]
                OuterCode = row[3]
            config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
            upperbound = np.log2(config_map.constellationN) * (float(config_map.outercodingrate)) * (
            float(config_map.innercodingrate))
            self.config_cursor.execute('INSERT INTO Egreedy (ID,TrialNumber,Mean,Lower,Upper,Eligibility) VALUES (?,?,?,?,?,?)',
                           (j, 0, 0, 0, upperbound, 1))

        self.config_connection.commit()

        self.config_cursor.execute('drop table if exists Boltzmann')
        self.config_connection.commit()

        sql = 'create table if not exists Boltzmann (ID integer primary key, TrialNumber integer default 0, Mean real default 0.0, Prob float default 1.0, Lower real default 0.0, Upper real default 0.0, Eligibility int default 1)'
        self.config_cursor.execute(sql)
        for j in xrange(1, Allconfigs + 1):
            self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [j])
            for row in self.config_cursor:
                Modulation = row[1]
                InnerCode = row[2]
                OuterCode = row[3]
                config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
            upperbound = np.log2(config_map.constellationN) * (float(config_map.outercodingrate)) * (
            float(config_map.innercodingrate))
            self.config_cursor.execute(
                'INSERT INTO Boltzmann (ID,TrialNumber,Mean,Prob,Lower,Upper,Eligibility) VALUES (?,?,?,?,?,?,?)',
                (j, 0, 0, 1.0, 0, upperbound, 1))

        self.config_connection.commit()

        # Gittins
        self.config_cursor.execute('drop table if exists Gittins')
        self.config_connection.commit()
        sql = 'create table if not exists Gittins (ID integer primary key, TrialNumber integer default 0, Mean real default 0.0, Stdv real default 1.0, Indexx float default 0)'
        self.config_cursor.execute(sql)
        for j in xrange(1, Allconfigs + 1):
            self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [j])
            for row in self.config_cursor:
                Modulation = row[1]
                InnerCode = row[2]
                OuterCode = row[3]
                config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
            upperbound = np.log2(config_map.constellationN) * (float(config_map.outercodingrate)) * (
            float(config_map.innercodingrate))
            self.config_cursor.execute('INSERT INTO Gittins (ID,TrialNumber,Mean,Stdv,Indexx) VALUES (?,?,?,?,?)',
                           (j, 0, 0.0, 0.0, upperbound))

        self.config_connection.commit()

        # UCB
        self.config_cursor.execute('drop table if exists UCB')
        self.config_connection.commit()
        sql = 'create table if not exists UCB (ID integer primary key, TrialNumber integer default 0, Mean real default 0.0, Ind float default 0)'
        self.config_cursor.execute(sql)
        M = 64
        maxReward = np.log2(M)
        for j in xrange(1, Allconfigs + 1):
            self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [j])
            for row in self.config_cursor:
                Modulation = row[1]
                InnerCode = row[2]
                OuterCode = row[3]
                config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
            upperbound = np.log2(config_map.constellationN) * (float(config_map.outercodingrate)) * (
            float(config_map.innercodingrate))
            Mean = upperbound / maxReward
            bonus = np.sqrt(2 * np.log10(Allconfigs))
            ind = Mean + bonus
            self.config_cursor.execute('INSERT INTO UCB (ID,TrialNumber,Mean,Ind) VALUES (?,?,?,?)', (j, 1, Mean, ind))

        self.config_connection.commit()

    def reset_config_tables(self):
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
        conf_id = 1
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
        self.conf_id = conf_id
        self.modulation = modulation
        self.inner_code = inner_code
        self.outer_code = outer_code
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
        self.config_connection = sqlite3.connect('config.db', check_same_thread=False)
        self.config_cursor = self.config_connection.cursor()
        self.training_mode = True

    def __del__(self):
        self.config_connection.close()
        self.config_cursor.close()

    def epsilon_greedy(self, num_trial, epsilon):
        self.config_cursor.execute('SELECT MAX(ID) FROM CONFIG')
        num_configs = self.config_cursor.fetchone()[0]

        if num_trial <= 2*num_configs:
            self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [num_trial])
            for row in self.config_cursor:
                Modulation = row[1]
                InnerCode = row[2]
                OuterCode = row[3]
            config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
            if self.training_mode:
                "Training all configurations..."
                self.training_mode = False
            return config_map, config_map

        for j in xrange(0, num_configs):
            self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [j])
            for row in self.config_cursor:
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
                variance = (sqth / trialN) - (np.power(mean, 2))
                if variance < 0:
                    variance = 0
                config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
                maxp = np.log2(config_map.constellationN) * (float(config_map.outercodingrate)) * (
                float(config_map.innercodingrate))
                unsuccess = total - success
                PSR = float(success) / total
                self.config_cursor.execute('UPDATE egreedy set TrialNumber=?, Mean=? WHERE ID=?', [trialN, mean, j])
            if trialN > 1:
                RCI = self.CI(mean, variance, maxp, CONFIDENCE, trialN)
                lower = RCI[0]
                upper = RCI[1]
                self.config_cursor.execute('UPDATE egreedy set TrialNumber=? ,Mean=? ,Lower=? ,Upper=? WHERE ID=?',
                               [trialN, mean, lower, upper, j])
        self.config_connection.commit()

        self.config_cursor.execute('SELECT MAX(Mean) FROM Egreedy')
        muBest = self.config_cursor.fetchone()[0]
        print "muBest = ", muBest
        for j in xrange(1, num_configs + 1):
            self.config_cursor.execute('SELECT Upper FROM Egreedy WHERE ID=?', [j])
            upper = self.config_cursor.fetchone()[0]
            if upper < muBest:
                # FAST FIX! change 0 for quick fix to 1, makes all methods eligable
                self.config_cursor.execute('UPDATE Egreedy set Eligibility=? WHERE ID=?', [0, j])
            else:
                self.config_cursor.execute('UPDATE Egreedy set Eligibility=? WHERE ID=?', [1, j])
        self.config_connection.commit()

        self.config_cursor.execute('SELECT count(*) FROM Egreedy WHERE Mean=?', [muBest])
        NO = self.config_cursor.fetchone()[0]
        nn = random.randrange(1, NO + 1)
        self.config_cursor.execute('SELECT ID FROM Egreedy WHERE Mean=?', [muBest])
        j = 0
        for row in self.config_cursor:
            j = j + 1
            if j == nn:
                configN = row[0]
                self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [configN])
                for row1 in self.config_cursor:
                    NextConf2 = ConfigurationMap(row1[1], row1[2], row1[3], row1[0])
                    print "Configuration is"
                    config_map = ConfigurationMap(NextConf2.modulation, NextConf2.inner_code, NextConf2.outer_code)
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
            self.config_cursor.execute('SELECT count(*) FROM Egreedy')
            NO = self.config_cursor.fetchone()[0]
            nn = random.randrange(1, NO + 1)
            self.config_cursor.execute('SELECT ID FROM Egreedy')
            j = 0
            for row in self.config_cursor:
                j = j + 1
                if j == nn:
                    configN = row[0]
                    break

            self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [configN])
            for row in self.config_cursor:
                NextConf1 = ConfigurationMap(row[1], row[2], row[3], row[0])
                print "Configuration is"
                config_map = ConfigurationMap(NextConf1.modulation, NextConf1.inner_code, NextConf1.outer_code)
                print "Modulation is ", config_map.constellationN, config_map.modulationtype
                print "Inner Code is ", config_map.innercodingtype, ", and coding rate is ", config_map.innercodingrate
                print "Outer Code is ", config_map.outercodingtype, ", and coding rate is ", config_map.outercodingrate
                print "###############################\n\n"

        return NextConf1, NextConf2

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
