#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO:
# - 220 V-Lampen (code, real life)
# - Ablaufbalken unten, Warnicon, Willkommenicon etc.
# - Test Bewegungsmelder
# - Mehr Audio
# Later:
# - Rotator bewegen.
# - Stromspar-Strategie
import sys, os, math, random, signal, atexit
from libavg import avg
import time

import MonitorJSONRPC

try:
    import subprocess
except:
    subprocess = False

g_player = avg.Player.get()
g_logger = avg.Logger.get()

def playSound(Filename):
    # fix this playSound with the new framework
    pass

def changeMover(NewMover):
    global CurrentMover
    CurrentMover.onStop(NewMover)
    CurrentMover = NewMover
    CurrentMover.onStart()
    g_logger.trace(g_logger.APP, "Mover: "+str(Status))

class BodyScanner:
    def __powerOn(self):
        g_logger.trace(g_logger.APP, "Body scanner power on")
        #self.__setDataLine(avg.PARPORTDATA1, 1)
        #self.__setDataLine(avg.PARPORTDATA2, 1)
        self.__PowerTimeoutID = g_player.setTimeout(20000, self.disable)
#    def __setDataLineStatus(self):
#        if self.__bConnected:
#            self.ParPort.setControlLine(avg.CONTROL_STROBE, 0)
#            g_logger.trace(g_logger.APP, str(self.__DataLineStatus))
#            self.ParPort.setAllDataLines(self.__DataLineStatus)
#            self.ParPort.setControlLine(avg.CONTROL_STROBE, 1)
#            time.sleep(0.001)
#            self.ParPort.setControlLine(avg.CONTROL_STROBE, 0)
#        for i in range(8):
#            icon = g_player.getElementByID("line_icon_"+str(i+1))
#            if icon:
#                if (self.__DataLineStatus & 2**i) != 0:
#                    g_player.getElementByID("line_icon_"+str(i+1)).opacity = 0.3
#                else:
#                    g_player.getElementByID("line_icon_"+str(i+1)).opacity = 0.1
#	g_logger.trace(g_logger.APP, "Data lines: "+str(self.__DataLineStatus));
    def __lineToIndex(self, line):
        if line == avg.PARPORTDATA0:
            return 1
        elif line == avg.PARPORTDATA1:
            return 2
        elif line == avg.PARPORTDATA2:
            return 3
        elif line == avg.PARPORTDATA3:
            return 4
        elif line == avg.PARPORTDATA4:
            return 5 
        elif line == avg.PARPORTDATA5:
            return 6
        elif line == avg.PARPORTDATA6:
            return 7
        elif line == avg.PARPORTDATA7:
            return 8
        else:
            return 0
    def __setDataLine(self, line, value):
        #self.ParPort.setControlLine(avg.CONTROL_STROBE, 0)
        icon = g_player.getElementByID("line_icon_"+str(self.__lineToIndex(line)))
        if value:
            #self.ParPort.setDataLines(line)
            if icon:
                icon.opacity = 0.3
            self.__DataLineStatus |= line
        else:
            #self.ParPort.clearDataLines(line)
            if icon:
                icon.opacity = 0.1
            self.__DataLineStatus &= not(line)
        #self.ParPort.setControlLine(avg.CONTROL_STROBE, 1)
        time.sleep(0.001)
        #self.ParPort.setControlLine(avg.CONTROL_STROBE, 0)
#        self.__setDataLineStatus()
    def __init__(self):
        #self.ParPort = avg.ParPort()
        #self.ParPort.init("")
        self.bMotorOn = 0
        self.bMotorDir = 0
        #if self.ParPort.getStatusLine(avg.STATUS_PAPEROUT):
            #g_logger.trace(g_logger.APP, 
                    #"Parallel conrad relais board not found. Disabling body scanner.")
            #self.__bConnected = 0
        #else:
            #g_logger.trace(g_logger.APP, 
                    #"Parallel conrad relais board found. Enabling body scanner.")
            #self.__bConnected = 1
        self.lastMotorOnTime = time.time()
        self.lastMotorDirTime = time.time()
        self.__isScanning = 0
        self.__PowerTimeoutID = 0
        self.__DataLineStatus = 0
    def delete(self):
        self.powerOff()
    def powerOff(self):
        g_logger.trace(g_logger.APP, "Body scanner power off")
        #self.__setDataLine(avg.PARPORTDATA1, 0)
        #self.__setDataLine(avg.PARPORTDATA2, 0)
        if self.__PowerTimeoutID:
            g_player.clearInterval(self.__PowerTimeoutID)
        self.__isScanning = 0
    def disable(self):
        g_logger.trace(g_logger.APP, "Body scanner not deactivating by itself - disabling.")
        self.powerOff()
        self.__bConnected = 0
    def startScan(self):
        def moveInit():
            self.__setDataLine(avg.PARPORTDATA0, 1)
            g_logger.trace(g_logger.APP, "Body scanner move init")
        def moveInitDone():
            self.__setDataLine(avg.PARPORTDATA0, 0)
            self.__isScanning = 1
            g_logger.trace(g_logger.APP, "Body scanner move init done")
        self.__powerOn();
        g_player.setTimeout(400, moveInit)
        g_player.setTimeout(2500, moveInitDone) 
    def poll(self):
        def printPPLine(line, name):
            print name,
            #if self.ParPort.getStatusLine(line):
                #print ": off",
            #else:
                #print ":  on",
        def safeGetSignal(bLastValue, Line):
            #bNewValue = self.ParPort.getStatusLine(Line)
            if not (bNewValue == bLastValue):
                time.sleep(0.01)
                #bNewerValue = self.ParPort.getStatusLine(Line)
                if not(bNewerValue == bNewValue):
                    g_logger.trace(g_logger.APP, "Body scanner line bouncing.")
                return bNewerValue
            else:
                return bLastValue
        #bMotorDir = not(safeGetSignal(self.bMotorDir, avg.STATUS_ACK))
        #bMotorOn = safeGetSignal(self.bMotorOn, avg.STATUS_BUSY)
        #if bMotorOn != self.bMotorOn:
            #if bMotorOn:
                #g_logger.trace(g_logger.APP, "Body scanner motor on signal.")
            #else:
                #g_logger.trace(g_logger.APP, "Body scanner motor off signal.")
        #if bMotorDir != self.bMotorDir:
            #if bMotorDir:
                #g_logger.trace(g_logger.APP, "Body scanner moving down signal.")
            #else:
                #g_logger.trace(g_logger.APP, "Body scanner moving up signal.")
        #if bMotorDir != self.bMotorDir or bMotorOn != self.bMotorOn:
            #if not(bMotorOn):
                #g_logger.trace(g_logger.APP, "    --> Motor is off.")
            #else:
                #if bMotorDir:
                    #g_logger.trace(g_logger.APP, "    -> Moving down.")
                #else:
                    #g_logger.trace(g_logger.APP, "    -> Moving up.")
        #if not(self.bMotorDir) and bMotorDir:
            #self.__setDataLine(avg.PARPORTDATA0, 0)
	#self.bMotorOn = bMotorOn
        #self.bMotorDir = bMotorDir
        #if self.__isScanning and not(self.bMotorOn):
            #self.powerOff()
        ##if self.ParPort.getStatusLine(avg.STATUS_SELECT):
            #g_player.getElementByID("warn_icon_1").opacity=0.3;
        #else:
            #g_player.getElementByID("warn_icon_1").opacity=0.1;
        #if self.ParPort.getStatusLine(avg.STATUS_ERROR):
            #g_player.getElementByID("warn_icon_2").opacity=0.3;
        #else:
        g_player.getElementByID("warn_icon_2").opacity=0.1;
    def isUserInRoom(self):
        # (ParPort.SELECT == true) == weißes Kabel == Benutzer in Schleuse
        return False #self.__bConnected #or not(self.ParPort.getStatusLine(avg.STATUS_SELECT))
    def isUserInFrontOfScanner(self):
        return 0 
#        return self.__bConnected and not(self.ParPort.getStatusLine(avg.STATUS_ERROR))
    def isMovingDown(self):
        return self.bMotorDir and self.bMotorOn
#    def isScannerAtBottom(self):
#        return self.__bConnected and ParPort.getStatusLine(avg.STATUS_BUSY)
    def isScannerConnected(self):
        return False #self.__bConnected

class TopRotator:
    def rotateAussenIdle(self):
        aussen = g_player.getElementByID("warten_aussen")
        aussen.angle += 0.02
        if (aussen.angle > 2*3.14159): 
            aussen.angle -= 2*3.14159
    def rotateInnenIdle(self): 
        innen = g_player.getElementByID("warten_innen")
        innen.angle -= 0.06
        if (innen.angle < 0):
            innen.angle += 3.14159
    def rotateTopIdle(self): 
        self.rotateAussenIdle()
        self.rotateInnenIdle()

class BottomRotator:
    def __init__(self):
        self.CurIdleTriangle=0
        self.TrianglePhase=0
    
    def fadeOutTriangle(self, i): 
        node = g_player.getElementByID("idle"+str(i))
        node.opacity -= 0.02
        if (node.opacity < 0):
            node.opacity = 0

    def rotateBottom(self):
        for i in range(12):
            self.fadeOutTriangle(i)
        self.TrianglePhase += 1
        if (self.TrianglePhase > 8):
            self.TrianglePhase = 0
            node = g_player.getElementByID("idle"+str(self.CurIdleTriangle))
            node.opacity = 1.0
            self.CurIdleTriangle += 1
            if (self.CurIdleTriangle == 12):
                self.CurIdleTriangle = 0

class TextElement:
    def __init__(self, Title, ImageID, RahmenID, Text, AudioFile):
        self.Title = Title
        self.ImageID = ImageID
        self.RahmenID = RahmenID
        self.Text = Text
        self.AudioFile = AudioFile

class MessageArea:
    def __init__(self):
        self.__ImageIDs = []
        self.__TimeoutID = 0
    def calcTextPositions (self, TextElements, TitleColor, TextColor):
        def setTextLine(Line, Text, Font, Size, Color):
            CurTextNode = g_player.getElementByID("line"+str(Line))
            CurTextNode.text = Text
            CurTextNode.font = Font
            CurTextNode.fontsize = Size
            CurTextNode.color = Color
        self.__TextElements = TextElements
        self.__ImageIDs = []
        CurLine = 5
        for CurElem in TextElements:
            setTextLine(CurLine, CurElem.Title, "Eurostile", 18, TitleColor)
            g_player.getElementByID("line"+str(CurLine)).y -= 5
            self.__ImageIDs.append((CurLine, CurElem.RahmenID, CurElem.ImageID, 
                    CurElem.AudioFile))
            self.__CurImage = 0
            CurLine += 1
            for CurText in CurElem.Text:
                setTextLine(CurLine, CurText, "Arial", 15, 
                        TextColor)
                CurLine += 1
            CurLine += 2
        self.__CurLine = 5
        if not(self.__ImageIDs == []):
            self.__Phase = 0
        else:
            self.__Phase = 1
            
    def clear(self): 
        for i in range(30):
            node = g_player.getElementByID("line"+str(i))
            node.opacity=0
            node.fontsize=18
            node.font="Arial"
            node.color="FFFFFF"
            node.text=""
            node.y=i*21
        for Image in self.__ImageIDs:
            for i in range(2):
                if not(Image[i+1] == ""):
                    Img = g_player.getElementByID(Image[i+1])
                    if not(Img == None):
                        Img.opacity = 0
                    if type(Img) == type(Player.getElementByID("koerperscan")):
                        Img.stop()
        for ID in ["reiter5", "reiter6", "reiter7",
                "reiter5_weiss", "reiter6_weiss", "reiter7_weiss"]:
            g_player.getElementByID(ID).opacity = 0
        if self.__TimeoutID:
            g_player.clearInterval(self.__TimeoutID)

    def showNextLine(self):
        def showImage(Line, ID, Phase):
            if not(ID == ""):
                Image = g_player.getElementByID(ID)
                if not(Image == None):
                    if Phase in [0,2]:
                        Image.y = g_player.getElementByID("line"+str(Line)).y
                    else:
                        Image.y = g_player.getElementByID("line"+str(Line+1)).y
                    Image.opacity = 1
                    if type(Image) == type(Player.getElementByID("koerperscan")):
                        Image.y += 2
                        Image.play()
                        g_player.setTimeout(10, lambda: Image.pause())
            self.__TimeoutID = 0
        if self.__Phase == 0:
            numLines = len(self.__TextElements[self.__CurImage].Text)
            curReiterID = "reiter"+str(numLines+1)
            showImage(self.__ImageIDs[self.__CurImage][0], curReiterID, 0)
            self.__CurImage+=1
            if self.__CurImage == len(self.__ImageIDs):
                self.__Phase = 1
                self.__CurImage = 0
        elif self.__Phase == 1:
            curImageID = self.__ImageIDs[self.__CurImage]
            showImage(curImageID[0], curImageID[1], 1)
            self.__TimeoutID = g_player.setTimeout(100, 
                    lambda: showImage(curImageID[0], curImageID[2], 1))
            self.__CurImage+=1
            if self.__CurImage == len(self.__ImageIDs):
                self.__Phase = 2
                self.__CurImage = 0
        elif self.__CurLine < 30:
            g_player.getElementByID("line"+str(self.__CurLine)).opacity=1.0
            for ImageID in self.__ImageIDs:
                if ImageID[0] == self.__CurLine:
                    numLines = len(self.__TextElements[self.__CurImage].Text)
                    curReiterID = "reiter"+str(numLines+1)+"_weiss"
                    showImage(self.__ImageIDs[self.__CurImage][0], curReiterID, 2)
                    Image = g_player.getElementByID(self.__ImageIDs[self.__CurImage][2])
                    if type(Image) == type(Player.getElementByID("koerperscan")):
                        Image.play()
                    self.__CurImage+=1
                    if ImageID[3] != "":
                        playSound(ImageID[3])
            self.__CurLine += 1

class LeerMover:
    def __init__(self):
        global Status
        Status = LEER
    def onStart(self):
        pass
        #if subprocess:
        #    subprocess.call(["xset", "dpms", "force", "suspend"])
    def onFrame(self):
        pass
    def onStop(self, NewMover):
        pass
        #if subprocess:
        #    subprocess.call(["xset", "dpms", "force", "on"])

class UnbenutztMover:
    def __init__(self):
        global Status
        Status = UNBENUTZT
        self.WartenNode = g_player.getElementByID("warten")
        self.__LastUserTime = 0
    def onStart(self):
        self.WartenNode.opacity = 1
        self.WartenNode.x = 178
        self.WartenNode.y = 241
        g_player.getElementByID("idle").opacity = 1
        g_player.getElementByID("auflage_background").opacity = 1
        MessageArea.clear()
        global Scanner
        if not Scanner.isScannerConnected:
            self.TimeoutID = g_player.setTimeout(60000, 
                    lambda : changeMover(Unbenutzt_AufforderungMover()))
        BottomRotator.CurIdleTriangle=0
        BottomRotator.TrianglePhase=0
    def onFrame(self):
        TopRotator.rotateTopIdle()
        BottomRotator.rotateBottom()
        global Scanner
        if Scanner.isUserInFrontOfScanner():
            g_logger.trace(g_logger.APP, "User in front of scanner")
            now = time.time()
            if now-self.__LastUserTime > 20:
                changeMover(Unbenutzt_AufforderungMover())
                self.__LastUserTime = now
    def onStop(self, NewMover):
        if not Scanner.isScannerConnected:
                g_player.clearInterval(self.TimeoutID)
        
class Unbenutzt_AufforderungMover:
    def __init__(self):
        global Status
        Status = UNBENUTZT_AUFFORDERUNG

    def onStart(self): 
        self.AufforderungTopActive = 0
        self.AufforderungBottomActive = 0
    
    def onFrame(self):
        TopRotator.rotateTopIdle()

        for i in range(12):
            if not ((i == 0 and self.AufforderungBottomActive) or 
                    (i == 6 and self.AufforderungTopActive)):
                BottomRotator.fadeOutTriangle(i)
        
        BottomRotator.TrianglePhase += 1
        if BottomRotator.TrianglePhase > 8:
            if ((BottomRotator.CurIdleTriangle == 4 or 
                        BottomRotator.CurIdleTriangle == 10) and
                    self.AufforderungBottomActive and 
                    self.AufforderungTopActive):
                changeMover(AufforderungMover())
            if (not self.AufforderungTopActive or 
                    not self.AufforderungBottomActive): 
                node = g_player.getElementByID(
                        "idle"+str(BottomRotator.CurIdleTriangle))
                node.opacity = 1.0
            if (BottomRotator.CurIdleTriangle == 0): 
                self.AufforderungBottomActive = 1
            if (BottomRotator.CurIdleTriangle == 6):
                self.AufforderungTopActive = 1
            BottomRotator.TrianglePhase = 0
            BottomRotator.CurIdleTriangle += 1
            if (BottomRotator.CurIdleTriangle == 12):
                BottomRotator.CurIdleTriangle = 0


    def onStop(self, NewMover): 
        for i in range(12):
            if (i != 0 and i != 6): 
                anim.fadeOut(Player.getElementByID("idle"+str(i)), 300)
  

class AufforderungMover:
    def __init__(self):
        global Status
        Status = AUFFORDERUNG
        self.curTriOpacity = 1.0
        self.triOpacityDir = -1

    def onStart(self):
        g_player.getElementByID("aufforderung_bottom").opacity=1
        g_player.getElementByID("aufforderung_top").opacity=1
        playSound("bitteida.wav")
        self.StopTimeoutID = g_player.setTimeout(3000, 
                    lambda : changeMover(UnbenutztMover()))

    def onFrame(self): 
        TopRotator.rotateTopIdle()
        self.curTriOpacity += self.triOpacityDir*0.03
        if self.curTriOpacity > 1:
            self.curTriOpacity = 1
            self.triOpacityDir = -1
        elif self.curTriOpacity < 0.3:
            self.curTriOpacity = 0.3
            self.triOpacityDir = 1
        g_player.getElementByID("idle0").opacity = self.curTriOpacity
        g_player.getElementByID("idle6").opacity = self.curTriOpacity

    def onStop(self, NewMover):
        g_player.clearInterval(self.StopTimeoutID)
        anim.fadeOut(Player.getElementByID("aufforderung_bottom"), 300)
        anim.fadeOut(Player.getElementByID("aufforderung_top"), 300)
        anim.fadeOut(Player.getElementByID("idle0"), 3000)
        anim.fadeOut(Player.getElementByID("idle6"), 3000)


class LoginMover:
    user = ''
    def __init__(self, user):
        global Status

        Status = LOGIN
        self.user = user

        self.bRotateAussen = 1
        self.bRotateInnen = 1
        self.START = 0
        self.SCANNING = 1
        self.Phase = self.START
        
        self.ScanFrames = 0
        self.ScanningBottomNode = g_player.getElementByID("scanning_bottom")

    def onStart(self): 
        warten = g_player.getElementByID("warten")
        anim.LinearAnim(warten, "x", 600, 178, 620, 0, None)
        anim.LinearAnim(warten, "y", 600, 241, 10, 0, None)
        for i in range(12):
            anim.fadeOut(Player.getElementByID("idle"+str(i)), 200)
        self.ScanningBottomNode.y = 600
        #Player.getElementByID("idle").opacity = 1
        #Player.getElementByID("auflage_background").opacity = 1
        #MessageArea.clear()
        #BottomRotator.CurIdleTriangle=0
        #BottomRotator.TrianglePhase=0
    
    def onFrame(self):
        global LastMovementTime
        TopRotator.rotateTopIdle()
        BottomRotator.rotateBottom()
        LastMovementTime = time.time()
        if (self.Phase == self.START):
            if (self.bRotateAussen):
                node = g_player.getElementByID("warten_aussen") 
                node.angle += 0.13
                TopRotator.rotateAussenIdle()
                if (abs(node.angle) < 0.3): 
                    node.angle = 0
                    self.bRotateAussen = 0
            if (self.bRotateInnen):
                node = g_player.getElementByID("warten_innen") 
                node.angle -= 0.07
                TopRotator.rotateInnenIdle()
                if (abs(node.angle) < 0.2):
                    node.angle = 0
                    self.bRotateInnen = 0
            if (not self.bRotateInnen and not self.bRotateAussen):
                anim.fadeOut(Player.getElementByID("warten"), 200)
                #node = g_player.getElementByID("line1")
                #node.text="scanning"
                #node.weight="bold"
                #anim.fadeIn(node, 1000, 1.0)
                #Player.getElementByID("line1").font="Eurostile"
                #anim.fadeIn(Player.getElementByID("balken_ueberschriften"), 300, 1.0)
                self.Phase = self.SCANNING
        elif (self.Phase == self.SCANNING):    
            self.ScanFrames += 1
            if (self.ScanFrames == 1):
                # TODO: show login message
                CurTextNode = g_player.getElementByID("loginMessage1")
                CurTextNode.text = 'Hallo %s,' % self.user
                CurTextNode.opacity = 1.0
                CurTextNode = g_player.getElementByID("loginMessage2")
                CurTextNode.opacity = 1.0
                CurTextNode = g_player.getElementByID("loginMessage3")
                CurTextNode.opacity = 1.0
                #Player.getElementByID("hand42").opacity=1.0
                #Player.getElementByID("start_scan_aufblitzen").opacity=1.0
                playSound("bioscan.wav")
                #node = g_player.getElementByID("handscanvideo")
                #node.opacity=1.0
                #node.play()
            elif (self.ScanFrames == 240):
                g_player.getElementByID("hand42").opacity=0.0
                changeMover(UnbenutztMover())
            #self.ScanningBottomNode.y -= 2.5 
    
    def onStop(self, NewMover):
        def setLine1Font():
            g_player.getElementByID("line1").font="Arial"
        g_player.getElementByID("loginMessage1").opacity=0.0
        g_player.getElementByID("loginMessage2").opacity=0.0
        g_player.getElementByID("loginMessage3").opacity=0.0

        node = g_player.getElementByID("handscanvideo")
        node.stop()
        node.opacity = 0
        anim.fadeOut(Player.getElementByID("line1"), 300)
        g_player.setTimeout(300, setLine1Font) 
        anim.fadeOut(Player.getElementByID("balken_ueberschriften"), 300)
        anim.fadeOut(Player.getElementByID("warten"), 300)
        g_player.getElementByID("scanning_bottom").opacity=0
        g_player.getElementByID("handscan_balken_links").stop()
        g_player.getElementByID("handscan_balken_rechts").stop()
        anim.fadeOut(Player.getElementByID("auflage_lila"), 300)
        MessageArea.clear()
        g_player.getElementByID("start_scan_aufblitzen").opacity = 0
        g_player.getElementByID("balken_ueberschriften").opacity = 0

class HandscanMover:
    def __init__(self):
        global Status
        Status = HANDSCAN
        self.TextElements = [
                TextElement("moleculare structur", "molekuel", "rahmen_5x4",
                    [ "Electrische Felder &amp; Wellen",
                      "Quantenanalyse",
                      "Atomare Zusammensetzung",
                      "Datensynthese"], 
                      "handscan.wav"),
                TextElement("genetische transcription", "helix", "rahmen_3x5",
                    [ "Analyse der Alpha-Helix",
                      "Arten der Pilzgattung Candida",
                      "Mitochondrien",
                      "> von Crosophila",
                      "> höherer Pflanzen",
                      "> von Säugern"], 
                      ""),
                TextElement("lebensform &amp; hercunft", "welt", "rahmen_5x3",
                    [ "Abgleich mit dem cosmolab",
                      "> Welten der Sauerstoffatmer", 
                      "> Verbotene Welten",
                      "> Virtuelle Orte",
                      "> Träume"], 
                      "")
            ]
        self.bRotateAussen = 1
        self.bRotateInnen = 1
        self.START = 0
        self.SCANNING = 1
        self.Phase = self.START
        
        self.CurHand = 0
        self.ScanFrames = 0
        self.ScanningBottomNode = g_player.getElementByID("scanning_bottom")

    def onStart(self): 
        warten = g_player.getElementByID("warten")
        anim.LinearAnim(warten, "x", 600, 178, 620, 0, None)
        anim.LinearAnim(warten, "y", 600, 241, 10, 0, None)
        for i in range(12):
            anim.fadeOut(Player.getElementByID("idle"+str(i)), 200)
        self.ScanningBottomNode.y = 600
        MessageArea.calcTextPositions(self.TextElements, "CDF1C8", "FFFFFF")
    
    def onFrame(self):
        global LastMovementTime
        LastMovementTime = time.time()
        if (self.Phase == self.START):
            if (self.bRotateAussen):
                node = g_player.getElementByID("warten_aussen") 
                node.angle += 0.13
                TopRotator.rotateAussenIdle()
                if (abs(node.angle) < 0.3): 
                    node.angle = 0
                    self.bRotateAussen = 0
            if (self.bRotateInnen):
                node = g_player.getElementByID("warten_innen") 
                node.angle -= 0.07
                TopRotator.rotateInnenIdle()
                if (abs(node.angle) < 0.2):
                    node.angle = 0
                    self.bRotateInnen = 0
            if (not self.bRotateInnen and not self.bRotateAussen):
                anim.fadeOut(Player.getElementByID("warten"), 400)
                node = g_player.getElementByID("line1")
                node.text="scanning"
                node.weight="bold"
                anim.fadeIn(node, 1000, 1.0)
                g_player.getElementByID("line1").font="Eurostile"
                anim.fadeIn(Player.getElementByID("balken_ueberschriften"), 300, 1.0)
                self.Phase = self.SCANNING
        elif (self.Phase == self.SCANNING):    
            self.ScanFrames += 1
            if (self.ScanFrames > 72 and self.ScanFrames%6 == 0): 
                g_player.getElementByID("hand"+str(self.CurHand)).opacity=0.0
                self.CurHand = int(math.floor(random.random()*15))
                g_player.getElementByID("hand"+str(self.CurHand)).opacity=1.0

            if (self.ScanFrames%8 == 0 and self.ScanFrames > 15): 
                MessageArea.showNextLine()
            if (self.ScanFrames == 1):
                g_player.getElementByID("start_scan_aufblitzen").opacity=1.0
                playSound("bioscan.wav")
                anim.fadeIn(Player.getElementByID("scanning_bottom"), 200, 1.0)
                anim.fadeIn(Player.getElementByID("auflage_lila"), 200, 1.0)
                g_player.getElementByID("handscan_balken_links").play()
                g_player.getElementByID("handscan_balken_rechts").play()
                anim.fadeOut(Player.getElementByID("auflage_background"), 200)
            elif (self.ScanFrames == 6):
                anim.fadeOut(Player.getElementByID("start_scan_aufblitzen"), 100)
                node = g_player.getElementByID("handscanvideo")
                node.opacity=1.0
                node.play()
            elif (self.ScanFrames == 72):
                node = g_player.getElementByID("handscanvideo")
                node.stop()
                anim.fadeOut(Player.getElementByID("handscanvideo"), 600)
            elif (self.ScanFrames == 240):
                changeMover(KoerperscanMover())
#                if (random.random() > 0.2): 
#                    changeMover(KoerperscanMover())
#                else:
#                    changeMover(HandscanErkanntMover())
            self.ScanningBottomNode.y -= 2.5 
    
    def onStop(self, NewMover):
        def setLine1Font():
            g_player.getElementByID("line1").font="Arial"
        g_player.getElementByID("hand"+str(self.CurHand)).opacity=0.0
        node = g_player.getElementByID("handscanvideo")
        node.stop()
        node.opacity = 0
        anim.fadeOut(Player.getElementByID("line1"), 300)
        g_player.setTimeout(300, setLine1Font) 
        anim.fadeOut(Player.getElementByID("balken_ueberschriften"), 300)
        anim.fadeOut(Player.getElementByID("warten"), 300)
        g_player.getElementByID("scanning_bottom").opacity=0
        g_player.getElementByID("handscan_balken_links").stop()
        g_player.getElementByID("handscan_balken_rechts").stop()
        anim.fadeOut(Player.getElementByID("auflage_lila"), 300)
        MessageArea.clear()
        g_player.getElementByID("start_scan_aufblitzen").opacity = 0
        g_player.getElementByID("balken_ueberschriften").opacity = 0

   
class HandscanErkanntMover: 
    def __init__(self):
        global Status
        Status = HANDSCAN_ERKANNT
        self.WillkommenNode = g_player.getElementByID("willkommen_text")
        MessageArea.clear()

    def onStart(self):
        def newMover():
            global bMouseDown
            if (bMouseDown):
                changeMover(WeitergehenMover())
            else:
                changeMover(UnbenutztMover())
        anim.fadeIn(Player.getElementByID("willkommen_text"), 500, 1)
        anim.fadeIn(Player.getElementByID("green_screen"), 500, 1)
        anim.LinearAnim(Player.getElementByID("willkommen_text"), "x", 
                1000, 607, 73, 0, None)
        anim.LinearAnim(Player.getElementByID("willkommen_text"), "y", 
                1000, 675, 81, 0, None)
        anim.LinearAnim(Player.getElementByID("willkommen_text"), "width",
                1000, 330, 874, 0, None)
        anim.LinearAnim(Player.getElementByID("willkommen_text"), "height",
                1000, 13, 37, 0, None)
        anim.fadeIn(Player.getElementByID("auflage_gruen"), 500, 1)
        playSound("willkomm.wav")
        self.StopTimeoutID = g_player.setTimeout(4000, 
                newMover)
    
    def onFrame(self):
        global LastMovementTime
        LastMovementTime = time.time()

    def onStop(self, NewMover):
        g_player.clearInterval(self.StopTimeoutID)
        anim.fadeOut(Player.getElementByID("willkommen_text"), 500)
        anim.fadeOut(Player.getElementByID("green_screen"), 500)
        anim.fadeOut(Player.getElementByID("auflage_gruen"), 500)


class HandscanAbgebrochenMover:
    def __init__(self):
        global Status
        Status = HANDSCAN_ABGEBROCHEN
        MessageArea.clear()

    def onStart(self):
        self.TextElements = [
                TextElement("vorgang abgebrochen", "", "", # warn_icon
                    [ "Extremität zu früh entfernt",
                      "> Alpha-Helix nicht ercannt",
                      "> Unbecannte Macht",
                      "> Lebensform unbecannt",
                      "> Wiederholen, ignorieren, abbrechen?"],
                      ""),
                TextElement("nicht identifiziert", "", "", [],
                    "nichtide.wav")
            ]
        self.CurFrame = 0
        self.WartenNode = g_player.getElementByID("warten")
        MessageArea.calcTextPositions(self.TextElements, "F69679", "FA3C09")
        playSound("Beep2.wav")  
        self.WartenNode.opacity = 1
        self.WartenNode.x = 178
        self.WartenNode.y = 241
        g_player.getElementByID("idle").opacity = 1
        g_player.getElementByID("auflage_background").opacity = 1

    def onFrame(self): 
        global LastMovementTime
        LastMovementTime = time.time()
        if self.CurFrame%6 == 0:
            MessageArea.showNextLine()
        if self.CurFrame == 150:
            changeMover(UnbenutztMover())
        self.CurFrame += 1

    def onStop(self, NewMover): 
        MessageArea.clear()

class KoerperscanMover:
    def __startVideo(self):
        Node = g_player.getElementByID("koerperscan")
        Node.opacity=1
        Node.play()
    def __stopVideo(self):
        Node = g_player.getElementByID("koerperscan")
        Node.opacity=0
        Node.stop()
    def __init__(self):
        global Status
        Status = KOERPERSCAN
        self.TextElements = [
            TextElement("grundtonus", "grundtonus", "rahmen_3x5",
                [ "Topographie",
                  "> Gliedmaße",
                  "Topologie",
                  "Scelettaufbau",
                  "> Wirbelsäule",
                  "Organe und Innereien"],
                  "grundton.wav"),
            TextElement("zellen", "zellen", "rahmen_5x4",
                [ "Cerngrundbasisplasma",
                  "Chromatin",
                  "Ribosom",
                  "Endoplasmatisches Reticulum",
                  "Tunnelproteine"],
                  "zellen.wav"),
            TextElement("gehirn", "gehirn", "rahmen_4x4",
                [ "Thermaler PET scan",
                  "> Cerebraler Cortex",
                  "> Occipatalanalyse",
                  "Intelligenzquotient"],
                  "bakterie.wav")
            ]
        self.CurFrame = 0
        global Scanner

    def onStart(self): 
        MessageArea.calcTextPositions(self.TextElements, "CDF1C8", "FFFFFF")
        playSound("stehenbl.wav")
        self.__startVideo()
        Scanner.startScan()

    def onFrame(self):
        def __done():
            if random.random() < 0.5:
                changeMover(HandscanErkanntMover())
            else:
                changeMover(FremdkoerperMover())
        global LastMovementTime
        LastMovementTime = time.time()
        if self.CurFrame%9 == 0:
            MessageArea.showNextLine()
        if Scanner.isScannerConnected():
            if Scanner.isMovingDown():
                __done()
            if self.CurFrame == 20*30:
                __done()
        else:
            if self.CurFrame == 10*30:
                __done()
        self.CurFrame += 1

    def onStop(self, NewMover):
        print("stop bodyscan")
        self.__stopVideo()

class FremdkoerperMover:
    def __startVideo(self):
        Node = g_player.getElementByID("koerperscan_rueckwaerts")
        Node.opacity=1
        Node.play()
    def __stopVideo(self):
        Node = g_player.getElementByID("koerperscan_rueckwaerts")
        Node.pause()
    def __init__(self):
        global Status
        Status = FREMDKOERPER
        self.CurFrame = 0

    def onStart(self):
        self.__startVideo()
        playSound("Beep1.wav")
        g_player.getElementByID("overlay").opacity=0.8
        WhichFremdkoerper = int(math.floor(random.random()*3))
        g_logger.trace(g_logger.APP, "Fremdkoerper: "+str(WhichFremdkoerper))
        self.__Region=Player.getElementByID("fremdkoerper_region")
        self.__Text=Player.getElementByID("fremdkoerper_text")
        if WhichFremdkoerper==0:
            self.__Icon=Player.getElementByID("flugzeug")
            self.__Region.x=90
            self.__Region.y=300
            self.__Text.text="Bitte begeben sie sich in den bereich social engineering."
            self.__StopFrame=50
        elif WhichFremdkoerper==1:
            self.__Icon=Player.getElementByID("implantat")
            self.__Region.x=140
            self.__Region.y=280
            self.__Text.text="Bionisches Implantat entdeckt."
            self.__StopFrame=15
        else:
            self.__Icon=Player.getElementByID("mate")
            self.__Region.x=90
            self.__Region.y=300
            self.__Text.text="Glashaltiges Gebilde im Magen. Bitte begeben sie sich umgehend zur Biowaffenentsorgungsstation auf Ebene 5b."
            self.__StopFrame=50

    def onFrame(self):
        if self.CurFrame == self.__StopFrame:
            self.__stopVideo()
            Node = g_player.getElementByID("fremdkoerper_region")
            Node.opacity=1
            Node.x=90
            Node.y=300
            playSound("Beep1.wav")
        if self.CurFrame == 80:
            g_player.getElementByID("overlay_streifen").opacity=1
            g_player.getElementByID("achtung").opacity=1
            self.__Icon.opacity=1
            g_player.getElementByID("fremdkoerper_titel").opacity=1
            g_player.getElementByID("fremdkoerper_text").opacity=1
        if self.CurFrame == 300:
            if (bMouseDown):
                changeMover(WeitergehenMover())
            else:
                changeMover(UnbenutztMover())
        self.CurFrame += 1

    def onStop(self, NewMover):
        Node = g_player.getElementByID("koerperscan_rueckwaerts")
        Node.opacity=0
        g_player.getElementByID("fremdkoerper_region").opacity=0
        g_player.getElementByID("overlay").opacity=0
        g_player.getElementByID("overlay_streifen").opacity=0
        g_player.getElementByID("achtung").opacity=0
        self.__Icon.opacity=0
        g_player.getElementByID("fremdkoerper_titel").opacity=0
        g_player.getElementByID("fremdkoerper_text").opacity=0
        MessageArea.clear()
        Node = g_player.getElementByID("koerperscan_rueckwaerts")
        Node.stop()

class WeitergehenMover:
    def __init__(self):
        global Status
        Status = WEITERGEHEN
        self.TextElements = [
              TextElement("bitte weitergehen", "", "", [], "") # warn_icon
            ]
        self.CurFrame = 0

    def onStart(self):
        MessageArea.calcTextPositions(self.TextElements, "F69679", "FA3C09")
        playSound("weiterge.wav")

    def onFrame(self):
        global LastMovementTime
        LastMovementTime = time.time()
        BottomRotator.rotateBottom()
        if self.CurFrame%6 == 0: 
           MessageArea.showNextLine()
        if (self.CurFrame%100 == 0):
            playSound("weiterge.wav")
        self.CurFrame += 1

    def onStop(self, NewMover):
        MessageArea.clear()

LastMovementTime = time.time()

def onFrame():
    CurrentMover.onFrame()
    global LastMovementTime
    if (Scanner.isUserInRoom() or Scanner.isUserInFrontOfScanner() or 
            not(Scanner.isScannerConnected())):
        LastMovementTime = time.time()
    if not(Status == LEER) and time.time()-LastMovementTime > EMPTY_TIMEOUT:
        changeMover(LeerMover())
    if Status == LEER and time.time()-LastMovementTime < EMPTY_TIMEOUT:
        changeMover(UnbenutztMover())

def onKeyUp(Event):
    global LastMovementTime
    LastMovementTime = time.time()
    if Event.keystring == "1":
        if Status == LEER:
            changeMover(UnbenutztMover())

def onMouseDown(Event):
    global LastMovementTime
    LastMovementTime = time.time()
    global bMouseDown
    bMouseDown = 1
    if Status == LEER:
        changeMover(UnbenutztMover())
    if Status in [UNBENUTZT, UNBENUTZT_AUFFORDERUNG, AUFFORDERUNG]:
        changeMover(HandscanMover())

def onMouseUp(Event):
    global LastMovementTime
    LastMovementTime = time.time()
    global bMouseDown
    bMouseDown = 0
    if Status in [HANDSCAN, KOERPERSCAN]:
        print "MouseUp, HandscanAbgebrochen"
        changeMover(HandscanAbgebrochenMover())
    elif (Status == WEITERGEHEN):
        changeMover(UnbenutztMover())

def signalHandler(signum, frame):
    global LastSignalHandler
    cleanup()
    g_logger.trace(g_logger.APP, "Terminating on signal "+str(signum))
    g_player.stop() 

def cleanup():
    Scanner.delete()

def handle_jsonrpc():
    global bMouseDown
    bMouseDown = 0
    try:
        event = rpcqueue.get(False)
        user = event[1]
        #timestamp = event[2]
        if event[0] == "login":
            changeMover(LoginMover(user))
            #self.content.login(user).
        #elif event[0] == "logout"
            #self.content.logout(user)
        #elif event[0] == "message":
            #self.content.message(user)
        #else:
            #pass
    except: pass

jsonrpcserver, rpcqueue = MonitorJSONRPC.forkServer(port=9090)

scheduler = g_player.setInterval(500, handle_jsonrpc)

LEER, UNBENUTZT, UNBENUTZT_AUFFORDERUNG, AUFFORDERUNG, HANDSCAN, HANDSCAN_ABGEBROCHEN, \
HANDSCAN_ERKANNT, AUFFORDERUNG_KOERPERSCAN, KOERPERSCAN, FREMDKOERPER, KOERPERSCAN_ERKANNT, \
WEITERGEHEN, ALARM, LOGIN \
= range(14)

bDebug = not(os.getenv('CLEUSE_DEPLOY'))
if (bDebug):
    #Player.setResolution(0, 512, 0, 0) 
    #Player.setResolution(0, 800, 0, 0) 
    g_logger.setCategories(g_logger.APP |
                      g_logger.WARNING | 
                      g_logger.PROFILE |
#                      g_logger.PROFILE_LATEFRAMES |
                      g_logger.CONFIG |
#                      g_logger.MEMORY  |
#                      g_logger.BLTS    |
                      g_logger.EVENTS)
    EMPTY_TIMEOUT = 10 
else:
    g_player.setResolution(1, 0, 0, 0)
    g_player.showCursor(0)
    g_logger.setFileDest("/var/log/cleuse.log")
    g_logger.setCategories(g_logger.APP |
                      g_logger.WARNING | 
                      g_logger.PROFILE |
#                      g_logger.PROFILE_LATEFRAMES |
                      g_logger.CONFIG |
#                      g_logger.MEMORY  |
#                      g_logger.BLTS    |
                      g_logger.EVENTS)
    # Time without movement until we blank the screen & dim the lights.
    EMPTY_TIMEOUT = 60*5
g_player.loadFile("scanner.avg")
g_player.setInterval(10, onFrame)

Scanner = BodyScanner() 
g_player.setInterval(100, Scanner.poll)
LastSignalHandler = signal.signal(signal.SIGHUP, signalHandler)
LastSignalHandler = signal.signal(signal.SIGINT, signalHandler)
LastSignalHandler = signal.signal(signal.SIGQUIT, signalHandler)
LastSignalHandler = signal.signal(signal.SIGILL, signalHandler)
LastSignalHandler = signal.signal(signal.SIGABRT, signalHandler)
LastSignalHandler = signal.signal(signal.SIGFPE, signalHandler)
LastSignalHandler = signal.signal(signal.SIGSEGV, signalHandler)
LastSignalHandler = signal.signal(signal.SIGPIPE, signalHandler)
LastSignalHandler = signal.signal(signal.SIGALRM, signalHandler)
LastSignalHandler = signal.signal(signal.SIGTERM, signalHandler)

TopRotator = TopRotator()
BottomRotator = BottomRotator()
MessageArea = MessageArea()

Status = UNBENUTZT 
CurrentMover = UnbenutztMover()
#CurrentMover.onStart()

try:
#    g_player.setVBlankFramerate(2)
    #Player.setFramerate(25)
    #anim.init(Player)
    g_player.showCursor(False)
    g_player.play()
    Scanner.delete()
finally:
    cleanup()
