
simmode = True
debug = True
import time
if simmode == False:
    from adafruit_servokit import ServoKit
import os
import json
import signal
import math



# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
if simmode == False:
    kit = ServoKit(channels=16)
else:
    kit = []
    
jsonfile = os.path.join(os.getcwd() ,'roproto.json')
jsondataraw = open(jsonfile)
jsondata = json.load(jsondataraw)
sleeptime = (100/1000)
degreespersecond = 1

threshold = 2 #divide the distance into smaller steps

def gotopos(jsondata,kit,pos):
    checklimits(jsondata,kit,pos)

def checklimits(jsondata,kit,pos):
    for i in range(0,5):
        neglimittag = 'j' + str(i) + '_neglimit'
        poslimittag = 'j' + str(i) + '_poslimit'
        neglimitvalue = jsondata[neglimittag]
        poslimitvalue = jsondata[poslimittag]
        if pos[i] >= neglimitvalue:
            pos[i] = neglimitvalue
        if pos[i] <= poslimitvalue:
            pos[i] = poslimitvalue
    rotateservos(jsondata,kit,pos)
    return()

def rotateservos(jsondata,kit,pos):
    for i in range(0,5): 
        if simmode == False:
            kit.servo[i].angle = pos[i]
    if simmode != False or debug == True:
        print(pos)
    return()


##______HOMING_____###
homingpos = jsondata['homingpos']
gotopos(jsondata,kit,homingpos)
lastpos = homingpos
posarray = jsondata['posarray']

##determine the highest value and divide that so it becomes the stepthreshold
for position in posarray:
    commandpos = position
    posdiff = 0
    highestpos = 1
    for i in range(0,5):
        posdiff = lastpos[i] - commandpos[i]
        if posdiff <= 0:
            posdiff = posdiff * -1
        if posdiff >= highestpos:
            highestpos = posdiff  
    loopthreshold = round(highestpos/threshold,1)

    ## split the travel distance 
    for j in range(0,int(loopthreshold)):
        steppos = [0,0,0,0,0]    
        for i in range(0,5):    
            stepdist =  commandpos[i] - lastpos[i]
            if stepdist != 0:
                disttoadd = ((loopthreshold*threshold)/stepdist) * (j*threshold)
            else:
                disttoadd = 0
            steppos[i] = lastpos[i] + disttoadd
        gotopos(jsondata,kit,steppos)
        time.sleep(sleeptime)
    gotopos(jsondata,kit,commandpos)
    lastpos = commandpos
    
    
