#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, math, random
from libavg import *
from datetime import datetime, timedelta

sys.path.append('../')

curLine = 16

def newWelcome():
    global curLine
    curLine += 1
    textNode = g_Player.getElementByID("begruessungstext")
    if curLine >= textNode.getNumChildren():
        curLine = 0
    node = textNode.getChild(curLine)
    if curLine == 5 or curLine == 12:
        LinearAnim(node, "x", 10000, -150, 800, 0, None, newWelcome).start()
    else:
        LinearAnim(node, "x", 11500, 800, -400, 0, None, newWelcome).start()
        
def normalize(v):
    v = v - int(v)
    if v < 0:
        v = v + 1
    return v

def calcMoonAge(year, mon, day):
    # calculate the Julian date at 12h UT
    YY = year - int((12-mon)/10)
    MM = mon+9 
    if MM >= 12:
        MM = MM - 12
    K1 = int(365.25*(YY+4712))
    K2 = int(30.6*MM+0.5)
    K3 = int(int((YY/100)+49)*0.75)-38
    
    JD = K1+K2+day+59          # for dates in Julian calendar
    if JD > 2299160:
        JD = JD - K3         # for Gregorian calendar
    # calculate moon's age in days
    IP = normalize((JD-2451550.1)/29.530588853)
    return int(IP*29.53)
    
liftoffTime = datetime(2023,5,23)
timeVelocity = 0
lastMins = "" 
now = 0

def calcTime():
    global liftoffTime, timeVelocity, lastMins, now
    lasttime = now
    now = datetime.now()
    dateString = "stationsceit:  "+now.date().isoformat()
    g_Player.getElementByID("stationsdatum").text = dateString
    timeString = now.time().isoformat()[0:8]
    g_Player.getElementByID("stationszeit").text = timeString
    timeToStart = liftoffTime-now
    # This isn't really correct, but who's going to notice...
    mins = "%(#)02d" % {'#': long((timeToStart.seconds%3600)/60)}
    if mins != lastMins:
        years = "%(#)02d" % {'#': long(timeToStart.days/365)}
        months = "%(#)02d" % {'#': long((timeToStart.days%365)/30)}
        days = "%(#)02d" % {'#': long(timeToStart.days%30)}
        hours = "%(#)02d" % {'#': long(timeToStart.seconds/3600)}
        startString = "P"+years+"Y"+months+"M"+days+"DT"+hours+"H"+mins+"M"
        g_Player.getElementByID("zeit_bis_start").text = startString
        lastMins = mins
    secs = "%(#)02d" % {'#': long(timeToStart.seconds%60)}
    ms = "%(#)03d" % {'#': long(timeToStart.microseconds/1000)}
    g_Player.getElementByID("secs_bis_start").text = secs+"S"+ms+"MS"

    timeVelocity += random.random()-0.5
    if timeVelocity > 2:
        timeVelocity -= 0.1
    elif timeVelocity < -2:
        timeVelocity += 0.1
    if timeVelocity > 5:
        timeVelocity -= 0.2
    elif timeVelocity < -5:
        timeVelocity += 0.2
    if random.random() > 0.9995:
        timeVelocity = random.random()*100-50
    if lasttime != 0:
        liftoffTime += timedelta(0,timeVelocity*(now-lasttime).microseconds/1000000)

moonAge = -1

def calcMoon():
    global moonAge
    now = datetime.now().date()
    newMoonAge = calcMoonAge(now.year, now.month, now.day)
    if newMoonAge != moonAge:
        moonAge = newMoonAge
        moonNode = g_Player.getElementByID("mond")
        for i in range(0,moonNode.getNumChildren()):
            moonNode.getChild(i).opacity = 0
            moonNode.getChild(i).angle = 0
        if moonAge < 15:
            moonNode.getChild(moonAge).opacity = 1
        else:
            curNode = moonNode.getChild(29-moonAge)
            curNode.opacity = 1
            curNode.angle = 3.1415

def onframe():
    calcTime()
    calcMoon()

g_Player = avg.Player.get()
Log = avg.Logger.get()
bDebug = not(os.getenv('CLEUSE_DEPLOY'))
if (bDebug):
    g_Player.setResolution(0, 0, 0, 0) 
else:
    g_Player.setResolution(1, 0, 0, 0)
    g_Player.showCursor(0)
    Log.setFileDest("/var/log/cleuse.log")
Log.setCategories(Log.APP |
                  Log.WARNING | 
                  Log.PROFILE |
#                 Log.PROFILE_LATEFRAMES |
                  Log.CONFIG
#                 Log.MEMORY  |
#                 Log.BLTS    
#                  Log.EVENTS
                  )
Words.addFontDir("../../fonts")
g_Player.loadFile("monitor1.avg")
g_Player.setInterval(10, onframe)
g_Player.setTimeout(10, newWelcome)
g_Player.getElementByID("bkgndvideo").opacity = 0.4
g_Player.getElementByID("bkgndvideo").play()
g_Player.setVBlankFramerate(1)
g_Player.play()
