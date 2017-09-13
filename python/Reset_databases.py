import math
import sqlite3

from Configuration_map import *


def RESET_Tables(BW):
    connection = sqlite3.connect('config.db')
    cursor = connection.cursor()
    cursor.execute('SELECT MAX(ID) FROM CONFIG')
    Allconfigs = cursor.fetchone()[0]
    for i in xrange(1,Allconfigs+1):
        cursor.execute('UPDATE CONFIG SET TrialN=? ,TOTAL=? ,SUCCESS=? ,THROUGHPUT=? ,SQTh=? WHERE ID=?',[0,0,0,0.0,0.0,i])
    connection.commit()
    cursor.execute('drop table if exists Egreedy')
    connection.commit()
    sql='create table if not exists Egreedy (ID integer primary key, TrialNumber integer default 0, Mean integer default 0, Lower real default 0.0, Upper real default 0.0, Eligibility int default 1)'
    cursor.execute(sql)
    for j in xrange(1,Allconfigs+1):
        cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[j])
        for row in cursor:
            Modulation = row[1]
            InnerCode = row[2]
            OuterCode = row[3]
        C_map=Conf_map(Modulation,InnerCode,OuterCode)
        upperbound = math.log(C_map.constellationN,2) * BW * (float(C_map.outercodingrate)) * (float(C_map.innercodingrate))
        cursor.execute('INSERT INTO Egreedy (ID,TrialNumber,Mean,Lower,Upper,Eligibility) VALUES (?,?,?,?,?,?)',(j,0,0,0,upperbound,1))

    connection.commit()
    cursor.execute('drop table if exists Boltzmann')
    connection.commit()
    sql='create table if not exists Boltzmann (ID integer primary key, TrialNumber integer default 0, Mean real default 0.0, Prob float default 1.0, Lower real default 0.0, Upper real default 0.0, Eligibility int default 1)'
    cursor.execute(sql)
    for j in xrange(1,Allconfigs+1):
        cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[j])
        for row in cursor:
            Modulation = row[1]
            InnerCode = row[2]
            OuterCode = row[3]
        C_map=Conf_map(Modulation,InnerCode,OuterCode)
        upperbound = math.log(C_map.constellationN,2) * BW * (float(C_map.outercodingrate)) * (float(C_map.innercodingrate))
        cursor.execute('INSERT INTO Boltzmann (ID,TrialNumber,Mean,Prob,Lower,Upper,Eligibility) VALUES (?,?,?,?,?,?,?)',(j,0,0,1.0,0,upperbound,1))

    connection.commit()
    cursor.execute('drop table if exists Gittins')
    connection.commit()
    sql='create table if not exists Gittins (ID integer primary key, TrialNumber integer default 0, Mean real default 0.0, Stdv real default 1.0, Indexx float default 0)'
    cursor.execute(sql)
    for j in xrange(1,Allconfigs+1):
        cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[j])
        for row in cursor:
            Modulation = row[1]
            InnerCode = row[2]
            OuterCode = row[3]
        C_map=Conf_map(Modulation,InnerCode,OuterCode)
        upperbound = math.log(C_map.constellationN,2) * BW * (float(C_map.outercodingrate)) * (float(C_map.innercodingrate))
        cursor.execute('INSERT INTO Gittins (ID,TrialNumber,Mean,Stdv,Indexx) VALUES (?,?,?,?,?)',(j,0,0.0,0.0,upperbound))

    connection.commit()
    cursor.execute('drop table if exists UCB')
    connection.commit()
    sql='create table if not exists UCB (ID integer primary key, TrialNumber integer default 0, Mean real default 0.0, Ind float default 0)'
    cursor.execute(sql)
##    cursor.execute('SELECT Max(CONSTELLATION) FROM CONFIG')
    M = 64
    maxReward = math.log(M,2) * BW
    for j in xrange(1,Allconfigs+1):
        cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[j])
        for row in cursor:
            Modulation = row[1]
            InnerCode = row[2]
            OuterCode = row[3]
        C_map=Conf_map(Modulation,InnerCode,OuterCode)
        upperbound = math.log(C_map.constellationN,2) * BW * (float(C_map.outercodingrate)) * (float(C_map.innercodingrate))
        Mean = upperbound/maxReward
        bonus = math.sqrt(2*math.log(Allconfigs,10))
        ind = Mean + bonus
        cursor.execute('INSERT INTO UCB (ID,TrialNumber,Mean,Ind) VALUES (?,?,?,?)',(j,1,Mean,ind))

    connection.commit()
    
    cursor.close()
    connection.close()
