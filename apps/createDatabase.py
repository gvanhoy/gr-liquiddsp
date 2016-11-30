import time
import numpy as np
import random
import math
import sqlite3
from CE import *

######################################################################
conn=sqlite3.connect('config.db')
print "Opened database successfully";
conn.execute('''CREATE TABLE CONFIG
    (ID INT PRIMARY KEY         NOT NULL,
    MODULATION       INT        NOT NULL,
    Innercode        INT        NOT NULL,
    Outercode        INT        NOT NULL,
    TrialN           INT        NOT NULL,
    Total            INT        NOT NULL,
    Success          INT        NOT NULL,
    Throughput       REAL       NOT NULL,
    SQTh             REAL       NOT NULL);''')
print "Table created successfully";
conn=sqlite3.connect('config.db')
j=1
for m in xrange(0,11):
##    for i in xrange(0,7):
        for o in xrange(0,8):
            conn.execute('INSERT INTO CONFIG (ID,MODULATION,Innercode,Outercode,TrialN,Total,Success,Throughput,SQTh) \
                  VALUES (?, ?, 0, ?, 0, 0, 0, 0.0, 0.0)',(j, m, o));
            j=j+1
conn.commit()
conn.close()
print "Config Records created successfully";
#################################################################################################################################
conn=sqlite3.connect('rules.db')
print "Opened rules database successfully";
conn.execute('''CREATE TABLE rules1
    (idd  INT PRIMARY KEY       NOT NULL,
    ID               INT        NOT NULL,
    MODULATION       INT        NOT NULL,
    Innercode        INT        NOT NULL,
    Outercode        INT        NOT NULL);''')
print "rules Table created successfully";
conn=sqlite3.connect('rules.db')
conn.execute('INSERT INTO rules1 (idd,ID,MODULATION,Innercode,Outercode) \
      VALUES (1,1, 0, 0, 0)');
conn.execute('INSERT INTO rules1 (idd,ID,MODULATION,Innercode,Outercode) \
      VALUES (2,2, 0, 0, 0)');
conn.commit()
conn.close()
print "rules1 Records created successfully";
