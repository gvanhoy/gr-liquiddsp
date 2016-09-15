from CE import *
from Reset_databases import *


i=1
BW=200000
T=1000
epsilon=0.1
DiscountFactor=0.9
maxReward=0
RESET_Tables(BW)
Conf=EGreedy(i,epsilon,BW)
print "EGreedy"
print "conf1 ",Conf[1].modulation, Conf[1].innercode, Conf[1].outercode
print "conf0 ",Conf[0].modulation, Conf[0].innercode, Conf[0].outercode
print "\n##################### \n##################### \n"
Conf=Boltzmann(i,T,BW)
print "Boltzmann"
print "conf1 ",Conf[1].modulation, Conf[1].innercode, Conf[1].outercode
print "conf0 ",Conf[0].modulation, Conf[0].innercode, Conf[0].outercode
print "\n##################### \n##################### \n"
Conf=Gittins(i,DiscountFactor)
print "Gittins"
print "conf1 ",Conf[1].modulation, Conf[1].innercode, Conf[1].outercode
print "conf0 ",Conf[0].modulation, Conf[0].innercode, Conf[0].outercode
print "\n##################### \n##################### \n"
Conf=UCB(i,maxReward)
print "UCB"
print "conf1 ",Conf[1].modulation, Conf[1].innercode, Conf[1].outercode
print "conf0 ",Conf[0].modulation, Conf[0].innercode, Conf[0].outercode

##for i in xrange(0,11):
##    print i


for i in range(11):
	for j in range (8):
		k = (i)*(8)+j+1
		print k

