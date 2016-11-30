##
## Hamed Asadi
## Confidence Interval based on t distribution
###############################################################################################################################
## PLEASE DO "NOT" EDIT THIS FILE!
###############################################################################################################################

import numpy as np
import random
import math
import sqlite3
from scipy.stats import *

def CI(mean, variance, maxp, confidence, N):
    C = 1-((1-confidence)/2)
    std = math.sqrt(variance)
    coefficient=t.ppf(C, N-1)
    RCIl = mean - (coefficient*(std/math.sqrt(N)))
    if RCIl<0:
        RCIl=0

    RCIu = mean + (coefficient*(std/math.sqrt(N)))
    if RCIu>maxp:
        RCIu=maxp
    
    RCI = [RCIl,RCIu]
    return RCI
        
        

        
        
        
    
    
