#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, math
sys.path.append('/usr/local/lib/python2.4/site-packages/libavg')
import avg
from datetime import date

sys.path.append('../')
import anim

FRAMERATE = 25

def init(): 
    node = Player.getElementByID("trailer")
    node.play()
#    anim.Animation(node, "angle", -3.1415/2, 0, 2500)
    node.opacity=1

def start_logo(): 
    Player.getElementByID("c-wars").opacity = 1
    anim.fadeOut(Player.getElementByID("c-wars"), 3000)
    anim.Animation(Player.getElementByID("c-wars"), "x", 66, 40, 5000) 

def start_words1(): 
    anim.Animation(Player.getElementByID("moon"), "opacity", 0.0, 1.0, 1000)
    anim.Animation(Player.getElementByID("where_past"), 
            "opacity", 1.0, 0.0, 2000)

def start_words2():
    anim.Animation(Player.getElementByID("meets_future"), 
            "opacity", 1.0, 0.0, 2000)

def start_url(): 
    Player.getElementByID("www_c-wars_com").opacity = 1
    anim.fadeOut(Player.getElementByID("www_c-wars_com"), 1500)

def fadeout(): 
    Player.getElementByID("trailer").opacity=0.0
    Player.getElementByID("moon").opacity = 1
    anim.fadeOut(Player.getElementByID("moon"), 500)

def start_animation(): 
    Player.setTimeout(10, init)
    Player.setTimeout(2000, start_logo)
    Player.setTimeout(3000, start_words1)
    Player.setTimeout(4500, start_words2)
    Player.setTimeout(6000, start_url)
    Player.setTimeout(8500, fadeout)

Player = avg.Player()
Log = avg.Logger.get()
bDebug = not(os.getenv('CLEUSE_DEPLOY'))
if (bDebug):
    Player.setResolution(0, 0, 0, 0) 
else:
    Player.setResolution(1, 0, 0, 0)
    Player.showCursor(0)
    Log.setDestination("/var/log/cleuse.log")
Log.setCategories(Log.APP |
                  Log.WARNING | 
                  Log.PROFILE |
#                 Log.PROFILE_LATEFRAMES |
                  Log.CONFIG |
#                 Log.MEMORY  |
#                 Log.BLTS    |
                  Log.EVENTS)

Player.loadFile("trailer.avg")
anim.init(Player)
Player.setTimeout(10, start_animation)
Player.setInterval(12000, start_animation)
Player.play(FRAMERATE)

