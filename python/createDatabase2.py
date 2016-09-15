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
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (1, 0, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (2, 1, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (3, 2, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (4, 3, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (5, 4, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (6, 5, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (7, 6, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (8, 7, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (9, 8, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (10, 9, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (11, 10, 0, 0, 0, 0, 0, 0.0, 0.0)');
###############################################################
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (12, 0, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (13, 1, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (14, 2, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (15, 3, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (16, 4, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (17, 5, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (18, 6, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (19, 7, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (20, 8, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (21, 9, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (22, 10, 1, 0, 0, 0, 0, 0.0, 0.0)');
###############################################################
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (23, 0, 2, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (24, 1, 2, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (25, 2, 2, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (26, 3, 2, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (27, 4, 2, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (28, 5, 2, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (29, 6, 2, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (30, 7, 2, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (31, 8, 2, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (32, 9, 2, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (33, 10, 2, 0, 0, 0, 0, 0.0, 0.0)');
###############################################################
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (34, 0, 3, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (35, 1, 3, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (36, 2, 3, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (37, 3, 3, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (38, 4, 3, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (39, 5, 3, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (40, 6, 3, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (41, 7, 3, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (42, 8, 3, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (43, 9, 3, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (44, 10, 3, 0, 0, 0, 0, 0.0, 0.0)');
###############################################################
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (45, 0, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (46, 1, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (47, 2, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (48, 3, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (49, 4, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (50, 5, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (51, 6, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (52, 7, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (53, 8, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (54, 9, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (55, 10, 4, 0, 0, 0, 0, 0.0, 0.0)');
###############################################################
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (56, 0, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (57, 1, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (58, 2, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (59, 3, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (60, 4, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (61, 5, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (62, 6, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (63, 7, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (64, 8, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (65, 9, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (66, 10, 5, 0, 0, 0, 0, 0.0, 0.0)');
###############################################################
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (67, 0, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (68, 1, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (69, 2, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (70, 3, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (71, 4, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (72, 5, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (73, 6, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (74, 7, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (75, 8, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (76, 9, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (77, 10, 6, 0, 0, 0, 0, 0.0, 0.0)');
###############################################################
###############################################################
###############################################################
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (1, 0, 0, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (2, 1, 0, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (3, 2, 0, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (4, 3, 0, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (5, 4, 0, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (6, 5, 0, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (7, 6, 0, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (8, 7, 0, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (9, 8, 0, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (10, 9, 0, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (11, 10, 0, 1, 0, 0, 0, 0.0, 0.0)');
###############################################################
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (12, 0, 1, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (13, 1, 1, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (14, 2, 1, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (15, 3, 1, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (16, 4, 1, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (17, 5, 1, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (18, 6, 1, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (19, 7, 1, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (20, 8, 1, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (21, 9, 1, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (22, 10, 1, 1, 0, 0, 0, 0.0, 0.0)');
###############################################################
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (23, 0, 2, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (24, 1, 2, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (25, 2, 2, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (26, 3, 2, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (27, 4, 2, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (28, 5, 2, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (29, 6, 2, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (30, 7, 2, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (31, 8, 2, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (32, 9, 2, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (33, 10, 2, 1, 0, 0, 0, 0.0, 0.0)');
###############################################################
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (34, 0, 3, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (35, 1, 3, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (36, 2, 3, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (37, 3, 3, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (38, 4, 3, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (39, 5, 3, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (40, 6, 3, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (41, 7, 3, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (42, 8, 3, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (43, 9, 3, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (44, 10, 3, 1, 0, 0, 0, 0.0, 0.0)');
###############################################################
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (45, 0, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (46, 1, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (47, 2, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (48, 3, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (49, 4, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (50, 5, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (51, 6, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (52, 7, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (53, 8, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (54, 9, 4, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (55, 10, 4, 0, 0, 0, 0, 0.0, 0.0)');
###############################################################
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (56, 0, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (57, 1, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (58, 2, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (59, 3, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (60, 4, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (61, 5, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (62, 6, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (63, 7, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (64, 8, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (65, 9, 5, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (66, 10, 5, 0, 0, 0, 0, 0.0, 0.0)');
###############################################################
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (67, 0, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (68, 1, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (69, 2, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (70, 3, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (71, 4, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (72, 5, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (73, 6, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (74, 7, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (75, 8, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (76, 9, 6, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (77, 10, 6, 0, 0, 0, 0, 0.0, 0.0)');

##      VALUES (4, "QAM", 0, 8, 0, 24, 0, 0, 0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (7, "PSK", 1, 2, 0, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (8, "PSK", 1, 4, 0, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (9, "PSK", 1, 8, 0, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (10, "PSK", 1, 2, 1, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (11, "PSK", 1, 4, 1, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (12, "PSK", 1, 8, 1, 1, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (13, "PSK", 0, 2, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (14, "PSK", 0, 4, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (15, "PSK", 0, 8, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (16, "PSK", 0, 2, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (17, "PSK", 0, 4, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (18, "PSK", 0, 8, 1, 0, 0, 0, 0, 0.0, 0.0)');
##conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING) \
##      VALUES (4, "QAM", 0, 8, 0, 24, 0, 0, 0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (19, "PSK", 1, 2, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (20, "PSK", 1, 4, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (21, "PSK", 1, 8, 0, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (22, "PSK", 1, 2, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (23, "PSK", 1, 4, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.execute('INSERT INTO CONFIG (ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING,TrialN,Total,Success,Throughput,SQTh) \
      VALUES (24, "PSK", 1, 8, 1, 0, 0, 0, 0, 0.0, 0.0)');
conn.commit()
conn.close()
print "Records created successfully";
#################################################################################################################################
conn=sqlite3.connect('rules.db')
print "Opened rules database successfully";
conn.execute('''CREATE TABLE rules1
    (idd  INT PRIMARY KEY       NOT NULL,
    ID               INT        NOT NULL,
    MODULATION       TEXT       NOT NULL,
    DIFFERENTIAL     INT        NOT NULL,
    CONSTELLATION    INT        NOT NULL,
    GRAY             INT        NOT NULL,
    CODING           INT        NOT NULL);''')
print "rules Table created successfully";
conn=sqlite3.connect('rules.db')
conn.execute('INSERT INTO rules1 (idd,ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING) \
      VALUES (1,1, "PSK", 0, 2, 0, 0)');
conn.execute('INSERT INTO rules1 (idd,ID,MODULATION,DIFFERENTIAL,CONSTELLATION,GRAY,CODING) \
      VALUES (2,2, "PSK", 0, 4, 0, 0)');
conn.commit()
conn.close()
print "rules1 Records created successfully";
#################################################################################################################################
conn=sqlite3.connect('SNR.db')
print "Opened SNR database successfully";
conn.execute('''CREATE TABLE snr
    (ID            INT        NOT NULL,
     snr           FLOAT      NOT NULL);''')
print "snr Table created successfully";
conn=sqlite3.connect('SNR.db')
conn.execute('INSERT INTO snr (ID,snr) \
      VALUES (1,0)');
conn.commit()
conn.close()
print "snr Records created successfully";
