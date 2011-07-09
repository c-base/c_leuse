#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, math, random, colorsys
sys.path.append('/usr/local/lib/python2.4/site-packages/libavg')
from libavg import avg

sys.path.append('../')
from libavg import anim

def interpolateColor(val, colors):
    i = 0
    maxVal, maxColor = colors[i]
    while maxVal < val:
        i += 1
        maxVal, maxColor = colors[i]
    if i == 0:
        resultColor = maxColor
    else:
        minVal, minColor = colors[i-1]
        ratio = (val-minVal)/(maxVal-minVal)
        resultColor = map(lambda min, max: ratio*(max-min)+min, minColor, maxColor)
    return "%(r)02X%(g)02X%(b)02X" % {
        'r': resultColor[0]*255, 'g': resultColor[1]*255, 'b': resultColor[2]*255 }

class Param:
    def __init__(self, name, unit, min, max, min_warning, max_warning, 
            precision):
        self.name = name
        self.unit = unit
        self.min = min
        self.max = max
        self.min_warning = min_warning
        self.max_warning = max_warning
        self.precision = precision
        self.cur = (max+min)/2
        self.__curspeed = 0
    def update(self):
        self.__curspeed += 0.0002*(random.random()-0.5) \
            *(self.max_warning-self.min_warning)- 0.03*self.__curspeed
        if self.cur > self.max_warning:
            self.__curspeed -= 0.00003
        if self.cur < self.min_warning:
            self.__curspeed += 0.00003
        self.cur += self.__curspeed
        if self.cur > self.max:
            self.cur = self.max
            if self.__curspeed > 0:
                self.__curspeed = 0
        if self.cur < self.min:
            self.cur = self.min
            if self.__curspeed < 0:
                self.__curspeed = 0
    def getColor(self):
        colors = [(self.min,         (0.4, 0, 0.5)), 
                  (self.min_warning, (0.14, 0, 0.5)),
                  ((self.max+self.min)/2, (0, 0.05, 0.3)),
                  (self.max_warning, (0.8, 0.05, 0)),
                  (self.max,         (0.7, 0.2, 0))
                 ]
        color = interpolateColor(self.cur, colors)
        return color

params = [[ Param("temp", "celvin", 261, 311, 280, 300, 0),
            Param("drucc", "Pa", 86990, 108570, 95000, 105000, 0),
            Param("leistung", "GW", 3560, 4400, 3600, 4380, 0),
            Param("masse", "t", 9003456, 9003479, 9003457, 9003478, 0)],
          [ Param("feuchtigceit", "%", 0, 100, 40, 60, 0),
            Param("chwercraft", "m/s<sup><span font_desc='10'>2</span></sup>",
                    9.75, 9.87, 9.80, 9.82, 2),
            Param("strahlung", "Bq", 0, 70, 1, 40, 0),
            Param("beleuchtung", "lx", 0, 208, 40, 195, 0)],
          [ Param("N<sub><span font_desc='10'>2</span></sub>", "%", 
                    70, 85, 74, 82, 3),
            Param("O<sub><span font_desc='10'>2</span></sub>", "%", 
                    17, 23, 19, 21, 3),
            Param("C<sub><span font_desc='10'>21</span></sub>H<sub><span font_desc='10'>30</span></sub>O<sub><span font_desc='10'>2</span></sub>", 
                    "%", 0.00, 0.02, 0.005, 0.019, 3),
            Param("CO<sub><span font_desc='10'>2</span></sub>", "%", 
                    0.01, 0.05, 0.025, 0.04, 3)]]

def initParams():
    def initBase(node, y):
        node.y = 81+24*y
        node.alignment = "right"
        node.color="0D1C45"
        node.opacity = 1
        node.parawidth = 300
        node.width = 300
        node.x -= 300
        node.font = "Eurostile"
        node.size = 14 
    for y in range(4):
        for x in range(3):
            id_base = "sys"+str(x+1)+str(y+1)
            label = Player.getElementByID(id_base+"_label")
            value = Player.getElementByID(id_base+"_value")
            if x == 0:
                label.x = 111
                value.x = 243
            elif x == 1:
                label.x = 418
                value.x = 528
            elif x == 2:
                label.x = 651
                value.x = 768
            initBase(label, y)
            initBase(value, y)
            param = params[x][y]

def onFrame():
    for y in range(4):
        for x in range(3):
            id_base = "sys"+str(x+1)+str(y+1)
            label = Player.getElementByID(id_base+"_label")
            value = Player.getElementByID(id_base+"_value")
            param = params[x][y]
            param.update()
            label.text = param.name+":"
            value.text = ("%(val)."+str(param.precision)+"f %(unit)s") % \
                {'val':param.cur, 'unit':param.unit}
            value.color = param.getColor()

Player = avg.Player.get()
Log = avg.Logger.get()
bDebug = not(os.getenv('CLEUSE_DEPLOY'))
if (bDebug):
    Player.setResolution(0, 0, 0, 0) 
else:
    Player.setResolution(1, 0, 0, 0)
    Player.showCursor(0)
    Log.setFileDest("/var/log/cleuse.log")
Log.setCategories(Log.APP |
                  Log.WARNING | 
                  Log.PROFILE |
#                 Log.PROFILE_LATEFRAMES |
                  Log.CONFIG 
#                 Log.MEMORY  |
#                 Log.BLTS    |
#                  Log.EVENTS
                 )

Player.loadFile("monitor2.avg")
anim.init(avg)
initParams()
framerate = 40
Player.setInterval(10, onFrame)
Player.getElementByID("bkgndvideo").opacity = 0.4
Player.getElementByID("bkgndvideo").play()
Player.setVBlankFramerate(1)
Player.play()

