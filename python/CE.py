##
## Hamed Asadi
## Cognitive Radio Engine and MetaCognitive Engine
############################################################################
## PLEASE DO "NOT" EDIT THIS FILE!
############################################################################

from CI import *
from ConfidenceInterval import *
from Configuration_map import *
from gittinsNormal import *
import sys

confidence = 0.9
PSR_Threshold = 0.8


############################################################################
class Conf (object):
    ID = 0
    modulation = 0
    innercode= 0
    outercode= 0

    def __init__(self,ID,modulation,innercode,outercode):
        self.ID = ID
        self.modulation = modulation
        self.innercode = innercode
        self.outercode = outercode

def make_Conf(ID,modulation,innercode,outercode):
    Configuration = Conf(ID,modulation,innercode,outercode)
    return Configuration


############################################################################
##  E-Greedy
############################################################################
def EGreedy(i, epsilon, BW):
  try:
    connection = sqlite3.connect('config.db')
    cursor = connection.cursor()
    cursor.execute('SELECT MAX(ID) FROM CONFIG')
    Allconfigs = cursor.fetchone()[0]
    for j in xrange(1,Allconfigs+1):
        cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[j])
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
            mean = throughput/trialN
            variance = (sqth/trialN)-(math.pow(mean, 2))
            if variance < 0:
                variance = 0
            C_map=Conf_map(Modulation,InnerCode,OuterCode)
            maxp = BW * math.log(C_map.constellationN,2) * (float(C_map.outercodingrate)) * (float(C_map.innercodingrate))
            unsuccess = total - success
            PSR = float(success)/total
            cursor.execute('UPDATE Egreedy set TrialNumber=? ,Mean=? WHERE ID=?',[trialN,mean,j])
        if trialN > 1:
            RCI = CI(mean, variance, maxp, confidence, trialN)
            lower = RCI[0]
            upper = RCI[1]
            cursor.execute('UPDATE Egreedy set TrialNumber=? ,Mean=? ,Lower=? ,Upper=? WHERE ID=?',[trialN,mean,lower,upper,j])
    connection.commit()
    
    cursor.execute('SELECT MAX(Mean) FROM Egreedy')
    muBest = cursor.fetchone()[0]
    print "muBest = ",muBest
    for j in xrange(1,Allconfigs+1):
        cursor.execute('SELECT Upper FROM Egreedy WHERE ID=?',[j])
        upper = cursor.fetchone()[0]
        if upper < muBest:
            # FAST FIX! change 0 for quick fix to 1, makes all methods eligable
            cursor.execute('UPDATE Egreedy set Eligibility=? WHERE ID=?',[0,j])
        else:
            cursor.execute('UPDATE Egreedy set Eligibility=? WHERE ID=?',[1,j])
    connection.commit()
    
    cursor.execute('SELECT count(*) FROM Egreedy WHERE Mean=?',[muBest])
    NO = cursor.fetchone()[0]
    nn = random.randrange(1,NO+1)
    cursor.execute('SELECT ID FROM Egreedy WHERE Mean=?',[muBest])
    j = 0
    for row in cursor:
        j = j+1
        if j==nn:
            configN=row[0]
            cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[configN])
            for row1 in cursor:
                NextConf2 = make_Conf(row1[0],row1[1],row1[2],row1[3])
                print "Configuration is"
                C_map=Conf_map(NextConf2.modulation,NextConf2.innercode,NextConf2.outercode)
                print "Modulation is ",C_map.constellationN,C_map.modulationtype
                print "Inner Code is ",C_map.innercodingtype,", and coding rate is ",C_map.innercodingrate
                print "Outer Code is ",C_map.outercodingtype,", and coding rate is ",C_map.outercodingrate
                print "###############################\n\n"
            break

    if random.random()>epsilon:
        print "***Exploitation***\n"
        NextConf1 = NextConf2

    else:
        print "***Exploration***\n"
        cursor.execute('SELECT count(*) FROM Egreedy')
        NO = cursor.fetchone()[0]
        nn = random.randrange(1,NO+1)
        cursor.execute('SELECT ID FROM Egreedy')
        j = 0
        for row in cursor:
            j = j+1
            if j == nn:
                configN=row[0]
                break                

        cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[configN])
        for row in cursor:
            NextConf1 = make_Conf(row[0],row[1],row[2],row[3])
            print "Configuration is"
            C_map=Conf_map(NextConf1.modulation,NextConf1.innercode,NextConf1.outercode)
            print "Modulation is ",C_map.constellationN,C_map.modulationtype
            print "Inner Code is ",C_map.innercodingtype,", and coding rate is ",C_map.innercodingrate
            print "Outer Code is ",C_map.outercodingtype,", and coding rate is ",C_map.outercodingrate
            print "###############################\n\n"

    cursor.close()
    connection.close()
    return NextConf1, NextConf2
  except:
      print "Error with database.", sys.exc_info()[0]
      cursor.close()
      connection.close()

############################################################################
## Boltzmann Strategy
############################################################################
def Boltzmann(i,T,BW):
  try:
    connection = sqlite3.connect('config.db')
    cursor = connection.cursor()
    cursor.execute('SELECT MAX(ID) FROM CONFIG')
    Allconfigs = cursor.fetchone()[0]
    for j in xrange(1,Allconfigs+1):
        cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[j])
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
            mean = throughput/trialN
            variance = (sqth/trialN) - (math.pow(mean,2))
            C_map=Conf_map(Modulation,InnerCode,OuterCode)
            maxp = BW * math.log(C_map.constellationN,2) * (float(C_map.outercodingrate)) * (float(C_map.innercodingrate))
            unsuccess = total - success
            PSR = float(success)/total
            cursor.execute('UPDATE Boltzmann set TrialNumber=? ,Mean=? WHERE ID=?',[trialN,mean,j])
        if trialN > 1 :
            RCI = CI(mean,variance,maxp,confidence,trialN)
            lower = RCI[0]
            upper = RCI[1]
            cursor.execute('UPDATE Boltzmann set TrialNumber=? ,Mean=? ,Lower=? ,Upper=? WHERE ID=?',[trialN,mean,lower,upper,j])
    connection.commit()
    cursor.execute('SELECT MAX(Mean) FROM Boltzmann')
    muBest = cursor.fetchone()[0]
    print "muBest = ",muBest
    for j in xrange(1,Allconfigs+1):
        cursor.execute('SELECT Upper FROM Boltzmann WHERE ID=?',[j])
        upper = cursor.fetchone()[0]
        if upper < muBest:
            cursor.execute('UPDATE Boltzmann set Eligibility=? ,Prob=? WHERE ID=?',[0,0,j])
        else:
            cursor.execute('UPDATE Boltzmann set Eligibility=? WHERE ID=?',[1,j])
    connection.commit()
 
    denominator = 0
    Allmeans = []
    IDS = []
    Pr = []
    k = 0
    cursor.execute('SELECT Mean,ID,Eligibility FROM Boltzmann')
    for row in cursor:
        if row[2]==1:
            k = k+1
            temp1 = row[0]
            temp2 = np.exp(temp1/T)
            Allmeans = np.append(Allmeans,temp2)
            IDS = np.append(IDS,row[1])
            denominator = denominator + temp2
    for j in xrange(1,k+1):
        temp = Allmeans[j-1]/denominator
        Pr = np.append(Pr,temp)
        cursor.execute('UPDATE Boltzmann set Prob=? WHERE ID=?',[Pr[j-1],IDS[j-1]])
    connection.commit()

##    cursor.executemany('UPDATE Boltzmann SET Prob=? WHERE ID=?', [(val,) for val in Pr,(x,) for x in IDS])
##    connection.commit()
    r = random.random()
    cursor.execute('SELECT Prob,ID FROM Boltzmann WHERE Eligibility=?',[1])
    for row in cursor:
        temp = row[0]
        if r<temp:
            configN = row[1]
            break
        else:
            r = r-temp
    
    cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[configN])
    for row1 in cursor:
        NextConf1 = make_Conf(row1[0],row1[1],row1[2],row1[3])
        print "Configuration is"
        C_map=Conf_map(NextConf1.modulation,NextConf1.innercode,NextConf1.outercode)
        print "Modulation is ",C_map.constellationN,C_map.modulationtype
        print "Inner Code is ",C_map.innercodingtype,", and coding rate is ",C_map.innercodingrate
        print "Outer Code is ",C_map.outercodingtype,", and coding rate is ",C_map.outercodingrate
        print "###############################\n\n"

    cursor.execute('SELECT count(*) FROM Boltzmann WHERE Mean=?',[muBest])
    NO = cursor.fetchone()[0]
    nn = random.randrange(1,NO+1)
    cursor.execute('SELECT ID FROM Boltzmann WHERE Mean=?',[muBest])
    j =0
    for row in cursor:
        j = j+1
        if j==nn:
            configN=row[0]
            cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[configN])
            for row1 in cursor:
                NextConf2 = make_Conf(row1[0],row1[1],row1[2],row1[3])
                print "Configuration is"
                C_map=Conf_map(NextConf2.modulation,NextConf2.innercode,NextConf2.outercode)
                print "Modulation is ",C_map.constellationN,C_map.modulationtype
                print "Inner Code is ",C_map.innercodingtype,", and coding rate is ",C_map.innercodingrate
                print "Outer Code is ",C_map.outercodingtype,", and coding rate is ",C_map.outercodingrate
                print "###############################\n\n"
            break
    cursor.close()
    connection.close()
    return NextConf1,NextConf2
  except:
    cursor.close()
    connection.close()

############################################################################
## Gittins Index
############################################################################
def Gittins(i,DiscountFactor):
  try:
    a = DiscountFactor
    connection = sqlite3.connect('config.db')
    cursor = connection.cursor()
    cursor.execute('SELECT MAX(ID) FROM CONFIG')
    Allconfigs = cursor.fetchone()[0]
    for j in xrange(1,Allconfigs+1):
        cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[j])
        for row in cursor:
            Modulation = row[1]
            InnerCode = row[2]
            OuterCode = row[3]
            trialN = row[4]
            total = row[5]
            success = row[6]
            throughput = row[7]
            sqth = row[8]
        if trialN > 1:
            mean = throughput/trialN
            variance = (sqth/trialN)-(math.pow(mean, 2))
            print "Variance", variance
            stdV = math.sqrt(variance)
            indexx = mean + (stdV*GittinsIndexNormalUnitVar(trialN,a))
            cursor.execute('UPDATE Gittins set TrialNumber=? ,Mean=? ,Stdv=? ,Indexx=? WHERE ID=?',[trialN,mean,stdV,indexx,j])
    connection.commit()
    cursor.execute('SELECT MAX(Mean) FROM Gittins')
    muBest = cursor.fetchone()[0]
    print "muBest = ",muBest
    cursor.execute('SELECT MAX(Indexx) FROM Gittins;')
    value = cursor.fetchone()[0]
    print "MAX Indexx = ",value
    cursor.execute('SELECT count(*) FROM Gittins WHERE Indexx=?',[value])
    NO = cursor.fetchone()[0]
    nn = random.randrange(1,NO+1)
    cursor.execute('SELECT ID FROM Gittins WHERE Indexx=?',[value])
    i =0
    for row in cursor:
        i = i+1
        if i==nn:
            configN=row[0]
            cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[configN])
            for row1 in cursor:
                NextConf1 = make_Conf(row1[0],row1[1],row1[2],row1[3])
                print "Configuration is"
                C_map=Conf_map(NextConf1.modulation,NextConf1.innercode,NextConf1.outercode)
                print "Modulation is ",C_map.constellationN,C_map.modulationtype
                print "Inner Code is ",C_map.innercodingtype,", and coding rate is ",C_map.innercodingrate
                print "Outer Code is ",C_map.outercodingtype,", and coding rate is ",C_map.outercodingrate
                print "###############################\n\n"
                
            break
    cursor.execute('SELECT count(*) FROM Gittins WHERE Mean=?',[muBest])
    NO = cursor.fetchone()[0]
    nn = random.randrange(1,NO+1)
    cursor.execute('SELECT ID FROM Gittins WHERE Mean=?',[muBest])
    j =0
    for row in cursor:
        j = j+1
        if j==nn:
            configN=row[0]
            cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[configN])
            for row1 in cursor:
                NextConf2 = make_Conf(row1[0],row1[1],row1[2],row1[3])
                print "Configuration is"
                C_map=Conf_map(NextConf2.modulation,NextConf2.innercode,NextConf2.outercode)
                print "Modulation is ",C_map.constellationN,C_map.modulationtype
                print "Inner Code is ",C_map.innercodingtype,", and coding rate is ",C_map.innercodingrate
                print "Outer Code is ",C_map.outercodingtype,", and coding rate is ",C_map.outercodingrate
                print "###############################\n\n"

            break

    cursor.close()
    connection.close()
    return NextConf1,NextConf2
  except:
    cursor.close()
    connection.close()

############################################################################
## Upper Confidence Bound 1 (UCB)
############################################################################
def UCB(i,maxReward):
  try:
    connection = sqlite3.connect('config.db')
    cursor = connection.cursor()
    cursor.execute('SELECT MAX(ID) FROM CONFIG')
    Allconfigs = cursor.fetchone()[0]
    cursor.execute('SELECT SUM(TrialN) FROM CONFIG')
    AllTrial = cursor.fetchone()[0]
    for j in xrange(1,Allconfigs+1):
        cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[j])
        for row in cursor:
            Modulation = row[1]
            InnerCode = row[2]
            OuterCode = row[3]
            trialN = row[4]
            total = row[5]
            success = row[6]
            throughput = row[7]
            sqth = row[8]
        if trialN == 0:
            cursor.execute('SELECT Mean FROM UCB WHERE ID=?',[j])
            mean = cursor.fetchone()[0]
        else:
            mean = (throughput/trialN)/maxReward
        AllT = Allconfigs + AllTrial
        bonus = math.sqrt((2*math.log(AllT,10))/(trialN+1))
        ind = mean+bonus          
        cursor.execute('UPDATE UCB set TrialNumber=? ,Mean=? ,Ind=? WHERE ID=?',[trialN+1,mean,ind,j])
    connection.commit()
    cursor.execute('SELECT MAX(Mean) FROM UCB')
    muBest = cursor.fetchone()[0]
    print "muBest = ",muBest
    cursor.execute('SELECT MAX(Ind) FROM UCB;')
    value = cursor.fetchone()[0]
    print "MAX Indexx = ",value
    cursor.execute('SELECT count(*) FROM UCB WHERE Ind=?',[value])
    NO = cursor.fetchone()[0]
    nn = random.randrange(1,NO+1)
    cursor.execute('SELECT ID FROM UCB WHERE Ind=?',[value])
    i =0
    for row in cursor:
        i = i+1
        if i==nn:
            configN=row[0]
            cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[configN])
            for row1 in cursor:
                NextConf1 = make_Conf(row1[0],row1[1],row1[2],row1[3])
                print "Configuration is"
                C_map=Conf_map(NextConf1.modulation,NextConf1.innercode,NextConf1.outercode)
                print "Modulation is ",C_map.constellationN,C_map.modulationtype
                print "Inner Code is ",C_map.innercodingtype,", and coding rate is ",C_map.innercodingrate
                print "Outer Code is ",C_map.outercodingtype,", and coding rate is ",C_map.outercodingrate
                print "###############################\n\n"
            break
    cursor.execute('SELECT count(*) FROM UCB WHERE Mean=?',[muBest])
    NO = cursor.fetchone()[0]
    nn = random.randrange(1,NO+1)
    cursor.execute('SELECT ID FROM UCB WHERE Mean=?',[muBest])
    j =0
    for row in cursor:
        j = j+1
        if j==nn:
            configN=row[0]
            cursor.execute('SELECT * FROM CONFIG WHERE ID=?',[configN])
            for row1 in cursor:
                NextConf2 = make_Conf(row1[0],row1[1],row1[2],row1[3])
                print "Configuration is"
                C_map=Conf_map(NextConf2.modulation,NextConf2.innercode,NextConf2.outercode)
                print "Modulation is ",C_map.constellationN,C_map.modulationtype
                print "Inner Code is ",C_map.innercodingtype,", and coding rate is ",C_map.innercodingrate
                print "Outer Code is ",C_map.outercodingtype,", and coding rate is ",C_map.outercodingrate
                print "###############################\n\n"
            break

    cursor.close()
    connection.close()
    return NextConf1,NextConf2
  except:
    cursor.close()
    connection.close()

############################################################################
## MetaCognitive Engine
############################################################################
##def MetaCE(i,conf,total,success,bad,Throughput,DiscountFactor):
