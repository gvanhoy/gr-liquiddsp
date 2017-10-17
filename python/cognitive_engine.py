#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2017 <Hamed Asadi, Garrett Vanhoy, University of Arizona>.
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
from scipy.stats import *

CONFIDENCE = 0.9
DiscountFactor = 0.9
window_size = 30
alpha = 0.2
initial_entropi = 0.0
BW = 100
c_epsilon = 1.0
dynamic_noise = 0.0

class cognitive_engine(gr.sync_block):
    """
    docstring for block cognitive_engine
    """
    def __init__(self, ce_type="", delayed_feedback="", delayed_strategy="", channel="", kindicator="", contextual_type="", noise=0):
        gr.sync_block.__init__(self,
            name="cognitive_engine",
            in_sig=[],
            out_sig=[])
        self.ce_type = ce_type
        self.delayed_feedback = delayed_feedback
        self.delayed_strategy = delayed_strategy
        self.channel = channel
        self.kindicator = kindicator
        self.contextual_type = contextual_type
        if self.contextual_type != "none":
            self.kindicator = "on"
            self.ce_type = "epsilon_greedy"
        if self.channel == "stationary":
            self.noise = noise
        else:
            self.noise = dynamic_noise
        self.database = DatabaseControl()

        self.database.reset_config_tables()
        self.database.reset_cognitive_engine_tables()

        self.engine = CognitiveEngine()
        self.knowledge = KnowledgeIndicator()
        self.message_port_register_in(pmt.intern('packet_info'))
        self.set_msg_handler(pmt.intern('packet_info'), self.handler)
        self.message_port_register_out(pmt.intern('configuration'))
        self.num_packets = 0
        self.initial_epsilon = 0.4
        self.TXperformance_matrix = np.zeros((1000, 3), dtype=np.float64)
        self.RXperformance_matrix = np.zeros((1000, 3), dtype=np.float64)
        self.PSR_Threshold = 0.6
        self.Throughput_Threshold = 1.5

    def handler(self, packet_info):
        self.num_packets += 1
        epsilon = 0.1
        DiscountFactor = 0.9
        modulation = pmt.to_python(pmt.dict_ref(packet_info, pmt.intern("modulation"), pmt.PMT_NIL))
        inner_code = pmt.to_python(pmt.dict_ref(packet_info, pmt.intern("inner_code"), pmt.PMT_NIL))
        outer_code = pmt.to_python(pmt.dict_ref(packet_info, pmt.intern("outer_code"), pmt.PMT_NIL))
        header_valid = pmt.to_python(pmt.dict_ref(packet_info, pmt.intern("header_valid"), pmt.PMT_NIL))
        payload_valid = pmt.to_python(pmt.dict_ref(packet_info, pmt.intern("payload_valid"), pmt.PMT_NIL))
        config_id = modulation*7*8 + inner_code*8 + outer_code + 1
        configuration = ConfigurationMap(modulation, inner_code, outer_code, config_id)
        goodput = np.log2(configuration.constellationN) * (float(configuration.outercodingrate)) * (float(configuration.innercodingrate)) * payload_valid
        if self.delayed_feedback == "no_delay":
            if modulation >= 0:
                if inner_code >= 0:
                    if outer_code >= 0:
                        self.database.write_configuration(self.ce_type, configuration,
                                                          header_valid,
                                                          payload_valid,
                                                          goodput, self.channel)
        elif self.delayed_feedback == "delay":
            if modulation >= 0:
                if inner_code >= 0:
                    if outer_code >= 0:
                        self.database.write_delayed_feedback(self.ce_type, configuration, header_valid, payload_valid,
                                                             goodput, self.channel)
        self.database.write_RX_result(config_id, self.num_packets, goodput, payload_valid)
        if self.kindicator == "on":
            self.knowledge.Knowledge_Indicators(self.num_packets, self.contextual_type, initial_entropi)

        if self.ce_type == "epsilon_greedy":
            if self.contextual_type == "none":
                ce_configuration = self.engine.epsilon_greedy(self.num_packets, epsilon, self.delayed_feedback,
                                                              self.delayed_strategy, self.channel)
            else:
                print "c_epsilon = ", c_epsilon
                ce_configuration = self.engine.epsilon_greedy(self.num_packets, c_epsilon, self.delayed_feedback,
                                                              self.delayed_strategy, self.channel)
        elif self.ce_type == "gittins":
            ce_configuration = self.engine.gittins(self.num_packets, DiscountFactor, self.delayed_feedback, self.delayed_strategy, self.channel)
        elif self.ce_type == "annealing_epsilon_greedy":
            ce_configuration = self.engine.annealing_epsilon_greedy(self.num_packets, self.initial_epsilon, self.delayed_feedback, self.delayed_strategy, self.channel)
            if self.initial_epsilon > 0.05:
                self.initial_epsilon -= 0.001
        elif self.ce_type == "RoTA":
            ce_configuration = self.engine.RoTA(self.num_packets, self.Throughput_Threshold, self.PSR_Threshold, self.delayed_feedback, self.delayed_strategy, self.channel)
        elif self.ce_type == "meta":
            if dynamic_noise > 0:
                SNratio = 10 * np.log10(np.power(0.05/(2*dynamic_noise), 2))
                if SNratio < 12:
                    ce_configuration = self.engine.epsilon_greedy(self.num_packets, epsilon, self.delayed_feedback, self.delayed_strategy, self.channel)
                elif SNratio < 18:
                    ce_configuration = self.engine.annealing_epsilon_greedy(self.num_packets, self.initial_epsilon, self.delayed_feedback, self.delayed_strategy, self.channel)
                else:
                    ce_configuration = self.engine.gittins(self.num_packets, DiscountFactor, self.delayed_feedback, self.delayed_strategy, self.channel)
            else:
                ce_configuration = self.engine.gittins(self.num_packets, DiscountFactor, self.delayed_feedback, self.delayed_strategy, self.channel)

        if ce_configuration is not None:
            new_configuration = pmt.make_dict()
            new_ce_configuration = ce_configuration[0]
            self.database.write_TX_result(self.ce_type, new_ce_configuration, self.num_packets, self.delayed_feedback, self.delayed_strategy, self.channel)
            new_configuration = pmt.dict_add(new_configuration, pmt.intern("modulation"), pmt.from_long(new_ce_configuration.modulation))
            new_configuration = pmt.dict_add(new_configuration, pmt.intern("inner_code"), pmt.from_long(new_ce_configuration.inner_code))
            new_configuration = pmt.dict_add(new_configuration, pmt.intern("outer_code"), pmt.from_long(new_ce_configuration.outer_code))
            self.message_port_pub(pmt.intern('configuration'), new_configuration)

    def get_number(self):
        if self.num_packets < 200:
            global dynamic_noise
            dynamic_noise = 0.0
            return dynamic_noise
        elif self.num_packets < 400:
            global dynamic_noise
            dynamic_noise = 0.006
            return dynamic_noise
        elif self.num_packets < 600:
            global dynamic_noise
            dynamic_noise = 0.02
            return dynamic_noise
        elif self.num_packets < 800:
            global dynamic_noise
            dynamic_noise = 0.01
            return dynamic_noise
        else:
            global dynamic_noise
            dynamic_noise = 0.0025
            return dynamic_noise

class DatabaseControl:
    def __init__(self):
        self.config_connection = sqlite3.connect('config.db', check_same_thread=False)
        self.config_cursor = self.config_connection.cursor()
        self.rules_connection = sqlite3.connect('rules.db', check_same_thread=False)
        self.rules_cursor = self.rules_connection.cursor()

    def __del__(self):
        self.config_connection.close()
        self.rules_connection.close()

    def write_RX_result(self, config_id, num_packets, throughput, PSR):
        self.config_cursor.execute('INSERT INTO rx (num_packets, config_id, throughput, PSR) VALUES (?,?,?,?)', (num_packets, config_id, throughput, PSR))
        self.config_cursor.execute('SELECT * FROM config WHERE ID=?', [config_id])
        for row in self.config_cursor:
            mean = float(row[7]) / row[4]
            PSR = row[11]
        self.config_cursor.execute('UPDATE tx SET known_mean=?, known_PSR=? WHERE config_id=?', [mean, PSR, config_id])
        self.config_connection.commit()

    def write_TX_result(self, ce_type, configuration, num_packets, delayed_feedback, delayed_strategy, channel):
        self.config_cursor.execute('SELECT * FROM config WHERE ID=?', [configuration.conf_id])
        for row in self.config_cursor:
            if delayed_strategy == "mean":
                if row[4] > 0:
                    sub_value = float(row[7]) / row[4]
                else:
                    sub_value = 0
            elif delayed_strategy == "lower":
                sub_value = row[9]
            elif delayed_strategy == "upper":
                sub_value = row[10]
            PSR = row[11]
            known_PSR = PSR
            if row[4] > 0:
                mean = float(row[7]) / row[4]
            else:
                mean = 0
        if delayed_feedback == "no_delay":
            sub_value = -1
            PSR = -1
        else:
            self.write_configuration(ce_type, configuration, 1, PSR, sub_value, channel)

        self.config_cursor.execute('INSERT INTO tx (num_packets, config_id, PSR, sub_value, over_write, known_mean, known_PSR) VALUES (?,?,?,?,?,?,?)', (num_packets, configuration.conf_id, PSR, sub_value, 0, mean, known_PSR))
        self.config_connection.commit()

    def write_delayed_feedback(self, ce_type, configuration, header_valid, payload_valid, goodput, channel):
        self.config_cursor.execute('SELECT Count(*) FROM tx WHERE config_id=? AND over_write=?', [configuration.conf_id, 0])
        row_count = self.config_cursor.fetchone()[0]
        if row_count > 0:
            self.config_cursor.execute('SELECT * FROM tx WHERE config_id=? AND over_write=?', [configuration.conf_id, 0])
            for row in self.config_cursor:
                sub_value = row[3]
                sub_PSR = row[2]
                no = row[0]
            d_PSR = payload_valid - sub_PSR
            d_goodput = goodput - sub_value
            self.config_cursor.execute('UPDATE tx SET over_write=? WHERE num_packets=?', (1, no))
            self.config_connection.commit()
            self.write_configuration(ce_type, configuration, 0, d_PSR, d_goodput, channel)
        else:
            self.write_configuration(ce_type, configuration, header_valid, payload_valid, goodput, channel)

    def write_configuration(self, ce_type, configuration, total, success, throughput, channel):
        self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [configuration.conf_id])
        has_row = False
        for row in self.config_cursor:
            Modulation = row[1]
            InnerCode = row[2]
            OuterCode = row[3]
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
            new_aggregated_Throughput = old_throughput + throughput
            # newThroughput = throughput
            newSQTh = old_sqth + np.power(throughput, 2)
            new_PSR = float(newSuccess + 1.0) / (newTotal + 2.0)
            Unsuccess = newTrialN - newSuccess
            PSRCI = self.PSR_CI(newSuccess, Unsuccess, CONFIDENCE)
            lowerP = PSRCI[0]
            upperP = PSRCI[1]
            if newTrialN == 1:
                mean = new_aggregated_Throughput / newTrialN
                variance = (newSQTh / newTrialN) - (np.power(mean, 2))
                self.config_cursor.execute('UPDATE CONFIG SET TrialN=? ,TOTAL=? ,SUCCESS=? ,THROUGHPUT=? ,SQTh=? ,LB_Throughput=? , PSR=? ,LB_PSR=? ,UB_PSR=?, Mean_Throughput=? WHERE ID=?',
                               [newTrialN, newTotal, newSuccess, new_aggregated_Throughput, newSQTh, 0.0, new_PSR, lowerP, upperP, mean,  configuration.conf_id])
            elif newTrialN > 1:
                if channel == "stationary":
                    mean = new_aggregated_Throughput / newTrialN
                    variance = (newSQTh / newTrialN) - (np.power(mean, 2))
                elif channel == "nonstationary":
                    if newTrialN > (1/alpha):
                        old_mean = old_throughput / num_trial
                        diff = throughput - old_mean
                        mean = old_mean + (alpha * diff)
                        old_variance = (old_sqth/num_trial) - (np.power(old_mean, 2))
                        variance = (1-alpha) * (old_variance + (alpha * np.power(diff, 2)))
                    else:
                        mean = new_aggregated_Throughput / newTrialN
                        variance = (newSQTh / newTrialN) - (np.power(mean, 2))
                if variance < 0:
                    variance = 0
                maxp = np.log2(configuration.constellationN) * (float(configuration.outercodingrate)) * (
                    float(configuration.innercodingrate))
                RCI = self.CI(mean, variance, maxp, CONFIDENCE, newTrialN)
                lowerM = RCI[0]
                upperM = RCI[1]
                self.config_cursor.execute(
                    'UPDATE CONFIG SET TrialN=? ,TOTAL=? ,SUCCESS=? ,THROUGHPUT=? ,SQTh=? ,LB_Throughput=? ,UB_Throughput=? ,PSR=? ,LB_PSR=? ,UB_PSR=?, Mean_Throughput=? WHERE ID=?',
                    [newTrialN, newTotal, newSuccess, new_aggregated_Throughput, newSQTh, lowerM, upperM, new_PSR, lowerP, upperP, mean, configuration.conf_id])
            if ce_type == "epsilon_greedy":
                if newTrialN == 1:
                    self.config_cursor.execute('UPDATE egreedy set TrialNumber=?, Mean=? WHERE ID=?',
                                                       [newTrialN, mean, configuration.conf_id])
                if newTrialN > 1:
                    self.config_cursor.execute(
                        'UPDATE egreedy set TrialNumber=? ,Mean=? ,Lower=? ,Upper=? WHERE ID=?',
                        [newTrialN, mean, lowerM, upperM, configuration.conf_id])
            elif ce_type == "gittins":
                if newTrialN == 1:
                    self.config_cursor.execute('UPDATE gittins set TrialNumber=?, Mean=? WHERE ID=?',
                                                       [newTrialN, mean, configuration.conf_id])
                if newTrialN > 1:
                    stdv = np.sqrt(variance)
                    index = mean + (stdv * self.GittinsIndexNormalUnitVar(newTrialN, DiscountFactor))
                    self.config_cursor.execute(
                        'UPDATE gittins set TrialNumber=? ,Mean=? ,stdv=? ,indexx=? WHERE ID=?',
                        [newTrialN, mean, stdv, index, configuration.conf_id])
            elif ce_type == "annealing_epsilon_greedy":
                if newTrialN == 1:
                    self.config_cursor.execute('UPDATE annealing_egreedy set TrialNumber=?, Mean=? WHERE ID=?',
                                               [newTrialN, mean, configuration.conf_id])
                if newTrialN > 1:
                    self.config_cursor.execute(
                        'UPDATE annealing_egreedy set TrialNumber=? ,Mean=? ,Lower=? ,Upper=? WHERE ID=?',
                        [newTrialN, mean, lowerM, upperM, configuration.conf_id])
            elif ce_type == "RoTA":
                if newTrialN == 1:
                    self.config_cursor.execute('UPDATE RoTA set TrialNumber=?, Mean=?, PSR=? WHERE ID=?',
                                                       [newTrialN, mean, new_PSR, configuration.conf_id])
                if newTrialN > 1:
                    stdv = np.sqrt(variance)
                    index = mean + (stdv * self.GittinsIndexNormalUnitVar(newTrialN, DiscountFactor))
                    self.config_cursor.execute(
                        'UPDATE RoTA set TrialNumber=? ,Mean=? ,lowerM=?, upperM=?, PSR=?, lowerP=?, upperP=?, indexx=? WHERE ID=?',
                        [newTrialN, mean, lowerM, upperM, new_PSR, lowerP, upperP, index, configuration.conf_id])

            self.config_connection.commit()

    def reset_cognitive_engine_tables(self):
        self.config_cursor.execute('SELECT MAX(ID) FROM CONFIG')
        Allconfigs = self.config_cursor.fetchone()[0]

        for i in xrange(1, Allconfigs + 1):
            self.config_cursor.execute('UPDATE CONFIG SET TrialN=? ,TOTAL=? ,SUCCESS=? ,THROUGHPUT=? ,SQTh=?, Mean_Throughput=? WHERE ID=?',
                           [0, 0, 0, 0.0, 0.0, 0.0, i])
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

        self.config_cursor.execute('drop table if exists Annealing_Egreedy')
        self.config_connection.commit()

        sql = 'create table if not exists Annealing_Egreedy (ID integer primary key, TrialNumber integer default 0, Mean integer default 0, Lower real default 0.0, Upper real default 0.0, Eligibility int default 1)'
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
                'INSERT INTO Annealing_Egreedy (ID,TrialNumber,Mean,Lower,Upper,Eligibility) VALUES (?,?,?,?,?,?)',
                (j, 0, 0, 0, upperbound, 1))

        self.config_connection.commit()

        # # Boltzmann
        # self.config_cursor.execute('drop table if exists Boltzmann')
        # self.config_connection.commit()
        #
        # sql = 'create table if not exists Boltzmann (ID integer primary key, TrialNumber integer default 0, Mean real default 0.0, Prob float default 1.0, Lower real default 0.0, Upper real default 0.0, Eligibility int default 1)'
        # self.config_cursor.execute(sql)
        # for j in xrange(1, Allconfigs + 1):
        #     self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [j])
        #     for row in self.config_cursor:
        #         Modulation = row[1]
        #         InnerCode = row[2]
        #         OuterCode = row[3]
        #         config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
        #     upperbound = np.log2(config_map.constellationN) * (float(config_map.outercodingrate)) * (
        #     float(config_map.innercodingrate))
        #     self.config_cursor.execute(
        #         'INSERT INTO Boltzmann (ID,TrialNumber,Mean,Prob,Lower,Upper,Eligibility) VALUES (?,?,?,?,?,?,?)',
        #         (j, 0, 0, 1.0, 0, upperbound, 1))
        #
        # self.config_connection.commit()

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

        # # UCB
        # self.config_cursor.execute('drop table if exists UCB')
        # self.config_connection.commit()
        # sql = 'create table if not exists UCB (ID integer primary key, TrialNumber integer default 0, Mean real default 0.0, Ind float default 0)'
        # self.config_cursor.execute(sql)
        # M = 64
        # maxReward = np.log2(M)
        # for j in xrange(1, Allconfigs + 1):
        #     self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [j])
        #     for row in self.config_cursor:
        #         Modulation = row[1]
        #         InnerCode = row[2]
        #         OuterCode = row[3]
        #         config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
        #     upperbound = np.log2(config_map.constellationN) * (float(config_map.outercodingrate)) * (
        #     float(config_map.innercodingrate))
        #     Mean = upperbound / maxReward
        #     bonus = np.sqrt(2 * np.log10(Allconfigs))
        #     ind = Mean + bonus
        #     self.config_cursor.execute('INSERT INTO UCB (ID,TrialNumber,Mean,Ind) VALUES (?,?,?,?)', (j, 1, Mean, ind))
        #
        # self.config_connection.commit()

        # RoTA
        self.config_cursor.execute('drop table if exists RoTA')
        self.config_connection.commit()
        sql = 'create table if not exists RoTA (ID integer primary key, TrialNumber integer default 0, Mean real default 0.0, LowerM real default 0.0, UpperM real default 0.0, PSR real default 1.0, LowerP real default 0.0, UpperP real default 0.0, Indexx float default 0, Eligibility int default 1)'
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
            self.config_cursor.execute('INSERT INTO RoTA (ID,TrialNumber,Mean,lowerM,upperM,PSR,lowerP,upperP,Indexx,Eligibility) VALUES (?,?,?,?,?,?,?,?,?,?)',
                                       (j, 0, 0.0, 0.0, upperbound, 1.0, 0.0, 1.0, upperbound, 1))

        self.config_connection.commit()

        # Decision Sequences
        self.config_cursor.execute('drop table if exists tx')
        self.config_connection.commit()
        sql = 'create table if not exists tx (num_packets integer primary key, config_id integer default 0, PSR real default -1.0, sub_value real default -1.0, over_write bit default 0, known_mean real default 0.0, known_PSR real default 0.0)'
        self.config_cursor.execute(sql)
        self.config_connection.commit()

        self.config_cursor.execute('drop table if exists rx')
        self.config_connection.commit()
        sql = 'create table if not exists rx (num_packets integer primary key, config_id integer default 0, throughput float default 0.0, PSR float default 0.0)'
        self.config_cursor.execute(sql)
        self.config_connection.commit()

        # Knowledge Indicators
        self.config_cursor.execute('drop table if exists KI')
        self.config_connection.commit()
        sql = 'create table if not exists KI (num_packets integer primary key, LBI real default 0.0, RBI real default 0.0, CCI real default 0.0, CI real default 0.0)'
        self.config_cursor.execute(sql)
        self.config_connection.commit()
        ent = 0
        for j in xrange(1, Allconfigs + 1):
            self.config_cursor.execute('SELECT LB_Throughput,UB_Throughput FROM config WHERE ID=?', [j])
            for row in self.config_cursor:
                lowerR = row[0]
                upperR = row[1]
            ent = ent + np.log(BW *(upperR - lowerR))
        global initial_entropi
        initial_entropi = ent

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
            SQTh             REAL       NOT NULL,
            LB_Throughput    REAL       NOT NULL,
            UB_Throughput    REAL       NOT NULL,
            PSR              REAL       NOT NULL,
            LB_PSR           REAL       NOT NULL,
            UB_PSR           REAL       NOT NULL,
            Mean_Throughput  REAL       NOT NULL);''')
        print "Table created successfully"
        conf_id = 1
        for m in xrange(0, 11):
            for i in xrange(0, 7):
                for o in xrange(0, 8):
                    config_map = ConfigurationMap(m, i, o)
                    upperbound = np.log2(config_map.constellationN) * (float(config_map.outercodingrate)) * (
                        float(config_map.innercodingrate))
                    self.config_connection.execute('INSERT INTO CONFIG (ID,MODULATION,Innercode,Outercode,TrialN,Total,Success,Throughput,SQTh,LB_Throughput,UB_Throughput,PSR,LB_PSR,UB_PSR,Mean_Throughput) \
                              VALUES (?, ?, ?, ?, 0, 0, 0, 0.0, 0.0, 0.0, ?, 1.0, 0.0, 1.0, 0.0)', (conf_id, m, i, o, upperbound))
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

    def CI(self, mean, variance, maxp, confidence, N):
        C = 1 - ((1 - confidence) / 2)
        std = np.sqrt(variance)
        coefficient = t.ppf(C, N - 1)
        RCIl = mean - (coefficient * (std / np.sqrt(N)))
        if RCIl < 0:
            RCIl = 0.0

        RCIu = mean + (coefficient * (std / np.sqrt(N))) + 0.0000001
        if RCIu > maxp:
            RCIu = maxp + 0.0000001
        RCI = [RCIl, RCIu]
        return RCI

    def PSR_CI(self, success, unsuccess, confidence):
        #if ((success > 100) or (unsuccess > 100)) or ((success > 20) and (unsuccess > 20)):
        [m, v] = beta.stats(success+1, unsuccess+1)
        std = np.sqrt(v)
        z = norm.ppf(confidence, 0, 1)
        lb = m - (z * std)
        if lb < 0:
            lb = 0.0
        ub = m + (z * std) + 0.0001
        if ub > 1.0:
            ub = 1.0
        PSRCI = [lb, ub]
        return PSRCI

    def GittinsIndexNormalUnitVar(self, No, Discount_F):
        Discount_F_index = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 0.995])
        No_index = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90,
                             100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 9999999])
        V_index = np.matrix([[0.14542, 0.17451, 0.20218, 0.22582, 0.23609, 0.22263, 0.15758, 0.12852],
                             [0.17209, 0.20815, 0.24359, 0.27584, 0.29485, 0.28366, 0.20830, 0.17192],
                             [0.18522, 0.22513, 0.26515, 0.30297, 0.32876, 0.32072, 0.24184, 0.20137],
                             [0.19317, 0.23560, 0.27874, 0.32059, 0.35179, 0.34687, 0.26709, 0.22398],
                             [0.19855, 0.24277, 0.28820, 0.33314, 0.36879, 0.36678, 0.28736, 0.24242],
                             [0.20244, 0.24801, 0.29521, 0.34261, 0.38200, 0.38267, 0.30429, 0.25803],
                             [0.20539, 0.25202, 0.30063, 0.35005, 0.39265, 0.39577, 0.31881, 0.27158],
                             [0.20771, 0.25520, 0.30496, 0.35607, 0.40146, 0.40682, 0.33149, 0.28356],
                             [0.20959, 0.25777, 0.30851, 0.36105, 0.40889, 0.41631, 0.34275, 0.29428],
                             [0.21113, 0.25991, 0.31147, 0.36525, 0.41526, 0.42458, 0.35285, 0.30400],
                             [.21867, .27048, .32642, .38715, .45047, .47295, .41888, .36986],
                             [.22142, .27443, .33215, .39593, .46577, .49583, .45587, .40886],
                             [.22286, .27650, .33520, .40070, .47448, .50953, .48072, .43613],
                             [.22374, .27778, .33709, .40370, .48013, .51876, .49898, .45679],
                             [.22433, .27864, .33838, .40577, .48411, .52543, .51313, .47324],
                             [.22476, .27927, .33932, .40728, .48707, .53050, .52451, .48677],
                             [.22508, .27974, .34003, .40843, .48935, .53449, .53391, .49817],
                             [.22534, .28011, .34059, .40934, .49117, .53771, .54184, .50796],
                             [.22554, .28041, .34104, .41008, .49266, .54037, .54864, .51648],
                             [.22646, .28177, .34311, .41348, .49970, .55344, .58626, .56637],
                             [.22678, .28223, .34381, .41466, .50219, .55829, .60270, .59006],
                             [.22693, .28246, .34416, .41525, .50347, .56084, .61220, .60436],
                             [.22703, .28260, .34438, .41561, .50425, .56242, .61844, .61410],
                             [.22709, .28270, .34452, .41585, .50478, .56351, .62290, .62123],
                             [.22714, .28276, .34462, .41602, .50516, .56431, .62629, .62674],
                             [.22717, .28281, .34470, .41615, .50545, .56493, .62896, .63116],
                             [.22720, .28285, .34476, .41625, .50568, .56543, .63121, .63481],
                             [.22722, .28288, .34480, .41633, .50587, .56583, .63308, .63789],
                             [.22741, .28316, .34524, .41714, .5092, .583, .65, .65]])
        j = 0
        for k in Discount_F_index:
            if k == Discount_F:
                a_i = j
                break
            j = j + 1
            ##    a_i = np.where(Discount_F_index==Discount_F)
        j = 0
        flag = 0
        for i in No_index:
            if i == No:
                n_i = j
                break
            elif i > No:
                n_i = j
                flag = 1
                break
            j = j + 1

        if flag == 1:
            v1 = V_index[n_i - 1, a_i]
            v2 = V_index[n_i, a_i]
            v = v1 + (v2 - v1) * ((No - No_index[n_i - 1]) / (No_index[n_i] - No_index[n_i - 1]))
        elif flag == 0:
            v = V_index[n_i, a_i]

        idx = v / (No * np.sqrt(1 - Discount_F))
        return idx


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
        self.database = DatabaseControl()
        # self.training_mode = True

    def __del__(self):
        self.config_connection.close()
        self.config_cursor.close()

    def epsilon_greedy(self, num_trial, epsilon, delayed_feedback, delayed_strategy, channel):
        self.config_cursor.execute('SELECT MAX(ID) FROM CONFIG')
        num_configs = self.config_cursor.fetchone()[0]

        # # Training Phase
        # if num_trial <= 2 * num_configs:
        #     temp = int(np.floor(num_trial/num_configs))
        #     index_no = num_trial - (temp * num_configs)
        #     if index_no == 0:
        #         index_no = 616
        #     if index_no > 616:
        #         index_no = 1
        #     print "num trial =", num_trial
        #     print "index_no = ", index_no
        #
        #     self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [index_no])
        #     for row in self.config_cursor:
        #         Modulation = row[1]
        #         InnerCode = row[2]
        #         OuterCode = row[3]
        #     config_map = ConfigurationMap(Modulation, InnerCode, OuterCode)
        #     if self.training_mode:
        #         "Training all configurations..."
        #         self.training_mode = False
        #     print "Training phase"
        #     print "Configuration is="
        #     print "Modulation is ", config_map.constellationN, config_map.modulationtype
        #     print "Inner Code is ", config_map.innercodingtype, ", and coding rate is ", config_map.innercodingrate
        #     print "Outer Code is ", config_map.outercodingtype, ", and coding rate is ", config_map.outercodingrate
        #     print "###############################\n\n"
        #     return config_map, config_map

        self.config_cursor.execute('SELECT MAX(Mean) FROM Egreedy')
        muBest = self.config_cursor.fetchone()[0]
        for j in xrange(1, num_configs + 1):
            self.config_cursor.execute('SELECT Upper FROM Egreedy WHERE ID=?', [j])
            upper = self.config_cursor.fetchone()[0]
            if upper < muBest:
                self.config_cursor.execute('UPDATE Egreedy set Eligibility=? WHERE ID=?', [0, j])
            else:
                self.config_cursor.execute('UPDATE Egreedy set Eligibility=? WHERE ID=?', [1, j])
        self.config_connection.commit()
        if random.random() > epsilon:
            print "***Exploitation***\n"
            print "num trial =", num_trial
            self.config_cursor.execute('SELECT count(*) FROM Egreedy WHERE Mean=?', [muBest])
            no = self.config_cursor.fetchone()[0]
            nn = random.randrange(1, no + 1)
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
            NextConf1 = NextConf2
        else:
            print "***Exploration***\n"
            print "num trial =", num_trial
            self.config_cursor.execute('SELECT count(*) FROM Egreedy WHERE Eligibility=?', [1])
            NO = self.config_cursor.fetchone()[0]
            nn = random.randrange(1, NO + 1)
            self.config_cursor.execute('SELECT ID FROM Egreedy WHERE Eligibility=?', [1])
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
            NextConf2 = NextConf1
        if delayed_feedback == "delay":
            self.config_cursor.execute('SELECT * FROM egreedy WHERE ID=?', [NextConf1.conf_id])
            for row in self.config_cursor:
                if delayed_strategy == "mean":
                    if row[1] == 0:
                        substitude_value = (row[3] + row[4]) / 2.0
                    else:
                        substitude_value = row[2]
                elif delayed_strategy == "lower":
                    substitude_value = row[3]
                elif delayed_strategy == "upper":
                    substitude_value = row[4]
            self.database.write_configuration("epsilon_greedy",NextConf1, 1, 1, substitude_value, channel)
        return NextConf1, NextConf2

    def annealing_epsilon_greedy(self, num_trial, epsilon, delayed_feedback, delayed_strategy, channel):
        self.config_cursor.execute('SELECT MAX(ID) FROM CONFIG')
        num_configs = self.config_cursor.fetchone()[0]

        self.config_cursor.execute('SELECT MAX(Mean) FROM annealing_Egreedy')
        muBest = self.config_cursor.fetchone()[0]
        # print "muBest = ", muBest
        for j in xrange(1, num_configs + 1):
            self.config_cursor.execute('SELECT Upper FROM annealing_Egreedy WHERE ID=?', [j])
            upper = self.config_cursor.fetchone()[0]
            if upper < muBest:
                self.config_cursor.execute('UPDATE annealing_Egreedy set Eligibility=? WHERE ID=?', [0, j])
            else:
                self.config_cursor.execute('UPDATE annealing_Egreedy set Eligibility=? WHERE ID=?', [1, j])
        self.config_connection.commit()
        if random.random() > epsilon:
            print "***Exploitation***\n"
            print "num trial =", num_trial
            self.config_cursor.execute('SELECT count(*) FROM annealing_Egreedy WHERE Mean=?', [muBest])
            no = self.config_cursor.fetchone()[0]
            nn = random.randrange(1, no + 1)
            self.config_cursor.execute('SELECT ID FROM annealing_Egreedy WHERE Mean=?', [muBest])
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
            NextConf1 = NextConf2
        else:
            print "***Exploration***\n"
            print "num trial =", num_trial
            self.config_cursor.execute('SELECT count(*) FROM annealing_Egreedy WHERE Eligibility=?', [1])
            no = self.config_cursor.fetchone()[0]
            nn = random.randrange(1, no + 1)
            self.config_cursor.execute('SELECT ID FROM annealing_Egreedy WHERE Eligibility=?', [1])
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
            NextConf2 = NextConf1
        if delayed_feedback == "delay":
            self.config_cursor.execute('SELECT * FROM annealing_Egreedy WHERE ID=?', [NextConf1.conf_id])
            for row in self.config_cursor:
                if delayed_strategy == "mean":
                    if row[1] == 0:
                        substitude_value = (row[3] + row[4]) / 2.0
                    else:
                        substitude_value = row[2]
                elif delayed_strategy == "lower":
                    substitude_value = row[3]
                elif delayed_strategy == "upper":
                    substitude_value = row[4]
            self.database.write_configuration("annealing_Egreedy",NextConf1, 1, 1, substitude_value, channel)
        return NextConf1, NextConf2

    def gittins(self, num_trial, DiscountFactor, delayed_feedback, delayed_strategy, channel):
        print "num trial =", num_trial
        self.config_cursor.execute('SELECT MAX(indexx) FROM gittins')
        highest_idx = self.config_cursor.fetchone()[0]

        self.config_cursor.execute('SELECT count(*) FROM gittins WHERE indexx=?', [highest_idx])
        no = self.config_cursor.fetchone()[0]
        nn = random.randrange(1, no + 1)
        self.config_cursor.execute('SELECT ID FROM gittins WHERE indexx=?', [highest_idx])
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
        NextConf1 = NextConf2
        if delayed_feedback == "delay":
            self.config_cursor.execute('SELECT * FROM config WHERE ID=?', [NextConf1.conf_id])
            for row in self.config_cursor:
                if delayed_strategy == "mean":
                    if row[4] > 0:
                        substitude_value = float(row[7]) / row[4]
                    else:
                        substitude_value = (row[9] + row[10]) / 2.0
                elif delayed_strategy == "lower":
                    substitude_value = row[9]
                elif delayed_strategy == "upper":
                    substitude_value = row[10]
            self.database.write_configuration("gittins",NextConf1, 1, 1, substitude_value, channel)
        return NextConf1, NextConf2

    def RoTA(self, num_trial, Throughput_Treshhold, PSR_Threshold, delayed_feedback, delayed_strategy, channel):
        window = num_trial - window_size
        self.config_cursor.execute('SELECT MAX(ID) FROM CONFIG')
        num_configs = self.config_cursor.fetchone()[0]
        for j in xrange(1, num_configs + 1):
            self.config_cursor.execute('SELECT UpperM, lowerM, upperP, lowerP FROM RoTA WHERE ID=?', [j])
            for row in self.config_cursor:
                upperM = row[0]
                lowerM = row[1]
                upperP = row[2]
                lowerP = row[3]

            if (upperM < Throughput_Treshhold) or (upperP < PSR_Threshold):
                self.config_cursor.execute('UPDATE RoTA set Eligibility=? WHERE ID=?', [0, j])
            elif (lowerM >= Throughput_Treshhold) and (lowerP >= PSR_Threshold):
                self.config_cursor.execute('UPDATE RoTA set Eligibility=? WHERE ID=?', [2, j])
            else:
                self.config_cursor.execute('UPDATE RoTA set Eligibility=? WHERE ID=?', [1, j])
        self.config_connection.commit()

        self.config_cursor.execute('SELECT Count(*) FROM RoTA WHERE Eligibility=?', [2])
        ofsseting_size = self.config_cursor.fetchone()[0]
        self.config_cursor.execute('SELECT Count(*) FROM RoTA WHERE Eligibility=?', [1])
        training_size = self.config_cursor.fetchone()[0]

        self.config_cursor.execute('SELECT Avg(throughput) FROM rx WHERE num_packets>?', [window])
        throughput_window = self.config_cursor.fetchone()[0]
        self.config_cursor.execute('SELECT Avg(PSR) FROM rx WHERE num_packets>?', [window])
        psr_window = self.config_cursor.fetchone()[0]
        print "num trial =", num_trial
        print "throughput_window = ", throughput_window
        print "psr_window = ", psr_window

        if ofsseting_size == 0:
            if training_size > 0:
                print "***Infant stage***\n"
                nn = random.randrange(1, training_size + 1)
                self.config_cursor.execute('SELECT ID FROM RoTA WHERE Eligibility=?', [1])
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
                NextConf2 = NextConf1
            else:
                print "***None of the Configurations are Qualified***\n"
                self.config_cursor.execute('SELECT MAX(Mean) FROM rota')
                maximum_potential = self.config_cursor.fetchone()[0]
                maximum_potential = maximum_potential - 0.0001
                print "max_potential = ", maximum_potential
                self.config_cursor.execute('SELECT ID FROM rota WHERE Mean>?', [maximum_potential])
                greedy_choice = self.config_cursor.fetchone()[0]
                self.config_cursor.execute('SELECT * FROM config WHERE ID=?', [greedy_choice])
                for row in self.config_cursor:
                    NextConf1 = ConfigurationMap(row[1], row[2], row[3], row[0])
                    print "Configuration is"
                    config_map = ConfigurationMap(NextConf1.modulation, NextConf1.inner_code, NextConf1.outer_code)
                    print "Modulation is ", config_map.constellationN, config_map.modulationtype
                    print "Inner Code is ", config_map.innercodingtype, ", and coding rate is ", config_map.innercodingrate
                    print "Outer Code is ", config_map.outercodingtype, ", and coding rate is ", config_map.outercodingrate
                    print "###############################\n\n"
                NextConf2 = NextConf1
        else:
            self.config_cursor.execute('SELECT Avg(known_mean) FROM tx WHERE num_packets>?', [window + 1])
            known_throughput_window = self.config_cursor.fetchone()[0]
            self.config_cursor.execute('SELECT Avg(known_PSR) FROM tx WHERE num_packets>?', [window + 1])
            known_psr_window = self.config_cursor.fetchone()[0]
            if (known_throughput_window > Throughput_Treshhold) and (training_size > 0) and (known_psr_window > PSR_Threshold):
                self.config_cursor.execute('SELECT MAX(indexx) FROM RoTA')
                highest_idx = self.config_cursor.fetchone()[0]
                self.config_cursor.execute('SELECT count(*) FROM RoTA WHERE indexx=?', [highest_idx])
                no = self.config_cursor.fetchone()[0]
                nn = random.randrange(1, no + 1)
                self.config_cursor.execute('SELECT ID FROM RoTA WHERE indexx=?', [highest_idx])
                j = 0
                for row in self.config_cursor:
                    j = j + 1
                    if j == nn:
                        configN = row[0]
                        self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [configN])
                        for row1 in self.config_cursor:
                            NextConf2 = ConfigurationMap(row1[1], row1[2], row1[3], row1[0])
                            print "Configuration is"
                            config_map = ConfigurationMap(NextConf2.modulation, NextConf2.inner_code,
                                                          NextConf2.outer_code)
                            print "Modulation is ", config_map.constellationN, config_map.modulationtype
                            print "Inner Code is ", config_map.innercodingtype, ", and coding rate is ", config_map.innercodingrate
                            print "Outer Code is ", config_map.outercodingtype, ", and coding rate is ", config_map.outercodingrate
                            print "###############################\n\n"
                        break
                NextConf1 = NextConf2
            else:
                self.config_cursor.execute('SELECT MAX(upperM) FROM RoTA WHERE Eligibility=?', [2])
                max_upperM = self.config_cursor.fetchone()[0]
                self.config_cursor.execute('SELECT ID FROM RoTA WHERE upperM=?', [max_upperM])
                ID_max_upperM = self.config_cursor.fetchone()[0]
                self.config_cursor.execute('SELECT * FROM CONFIG WHERE ID=?', [ID_max_upperM])
                for row1 in self.config_cursor:
                    NextConf2 = ConfigurationMap(row1[1], row1[2], row1[3], row1[0])
                    print "Configuration is"
                    config_map = ConfigurationMap(NextConf2.modulation, NextConf2.inner_code,
                                                  NextConf2.outer_code)
                    print "Modulation is ", config_map.constellationN, config_map.modulationtype
                    print "Inner Code is ", config_map.innercodingtype, ", and coding rate is ", config_map.innercodingrate
                    print "Outer Code is ", config_map.outercodingtype, ", and coding rate is ", config_map.outercodingrate
                    print "###############################\n\n"
                NextConf1 = NextConf2
        if delayed_feedback == "delay":
            self.config_cursor.execute('SELECT * FROM rota WHERE ID=?', [NextConf1.conf_id])
            for row in self.config_cursor:
                if delayed_strategy == "mean":
                    if row[1] == 0:
                        substitude_value = (row[3] + row[4]) / 2.0
                    else:
                        substitude_value = row[2]
                elif delayed_strategy == "lower":
                    substitude_value = row[3]
                elif delayed_strategy == "upper":
                    substitude_value = row[4]
            self.database.write_configuration("rota",NextConf1, 1, 1, substitude_value, channel)
        return NextConf1, NextConf2


class KnowledgeIndicator:
    def __init__(self):
        self.config_connection = sqlite3.connect('config.db', check_same_thread=False)
        self.config_cursor = self.config_connection.cursor()
        self.database = DatabaseControl()
        # self.training_mode = True

    def __del__(self):
        self.config_connection.close()
        self.config_cursor.close()

    def Knowledge_Indicators(self, num_trial, contextual_type, i_entropi):
        self.config_cursor.execute('SELECT MAX(ID),MAX(Mean_Throughput),MAX(UB_Throughput) FROM CONFIG')
        for row in self.config_cursor:
            num_configs = row[0]
            muBest = row[1]
            upperMAX = row[2]
        Nk = num_configs
        Ne = 0
        CCI_nominator = 0.0
        CCI_denominator = 0.0
        entropi = 0
        for j in xrange(1, num_configs + 1):
            self.config_cursor.execute('SELECT LB_Throughput,UB_Throughput FROM config WHERE ID=?', [j])
            for row in self.config_cursor:
                lowerR = row[0]
                upperR = row[1]
                CCI_denominator = CCI_denominator + (upperR - lowerR)
            if upperR > muBest:
                Ne = Ne + 1
                CCI_nominator = CCI_nominator + (upperR - muBest)
                entropi = entropi + np.log(BW * (upperR - lowerR))

        LBI = float((Nk - Ne)) / (Nk - 1)
        RBI = muBest / upperMAX
        CCI = 1 - (CCI_nominator / CCI_denominator)
        CI = 1 - (entropi / i_entropi)

        if contextual_type != "none":
            if contextual_type == "context_lbi":
                global c_epsilon
                c_epsilon = 1 - LBI
            elif contextual_type == "context_rbi":
                global c_epsilon
                c_epsilon = 1 - RBI
            elif contextual_type == "context_cci":
                global c_epsilon
                c_epsilon = 1 - CCI
            elif contextual_type == "context_ci":
                global c_epsilon
                c_epsilon = 1 - CI

        self.config_cursor.execute('INSERT INTO KI (num_packets, LBI, RBI, CCI, CI) VALUES (?,?,?,?,?)', (num_trial, LBI, RBI, CCI, CI))
        self.config_connection.commit()








