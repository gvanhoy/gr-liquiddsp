##
## Hamed Asadi
## Confidence Interval
###############################################################################################################################
## PLEASE DO "NOT" EDIT THIS FILE!
###############################################################################################################################

import numpy as np
import random
import math
import sqlite3
from scipy.stats import *

def ConfidenceInterval(Success, Unsuccess, confidence):
    a = Success
    b = Unsuccess
##    if (a>2000) or (b>2000) or ((a>20) and (b>20)):
##        ##m = float(a)/(a+b)
##        m, v = beta.stats(a, b, moments='mv')
##        std = np.sqrt(v)
##        z = norm.ppf(confidence)
##        LB = m.item(0)-z*std
##        UB = m.item(0)+z*std

    psl = 1- beta.ppf(1-((1-confidence)/2),b,a)
    psh = 1- beta.ppf(((1-confidence)/2),b,a)
    ps = [psl,psh]
    return ps
        
    
    
