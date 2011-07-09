#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys, os, math, socket, urllib2, re, datetime, time, random, thread
from libavg import avg, anim


shotNum = 0

def onkey(Event):
    global shotNum
    key = Event.keystring
    if key == "s":
        shotNum += 1
        Player.screenshot("infoscreen"+str(shotNum)+".png")

class Termin:
    def __init__(self, date, time, event):
        def escape(s):
            return s.replace("&", "&amp;")
        self.date = escape(date)
        self.time = escape(time)
        self.event = escape(event)
        print (self.date, self.time, self.event)

termine = []

def parse_termine():
    print "parse_termine"
    global termineStr
    global termine
    global termineBereit
    termine = []
    lines = termineStr.splitlines()
    expr = re.compile(
            "\|\|'''(.+)'''\|\|(.+)\|\|'''(.+)'''\|\|'''(.+)'''\|\|'''(.+)'''\|\|'''(.+)'''\|\|")
    for line in lines:
        line = line.rstrip("\n\r \t")
        match = expr.search(line)
        if match != None:
            if match.group(6) == "x" or match.group(6) == "xx":
                try:
                    date_struct = time.strptime(match.group(1), "%d.%m.%Y")
                    eventDate = datetime.date(date_struct.tm_year, date_struct.tm_mon, 
                            date_struct.tm_mday)
                    if match.group(6) == "x":
                        td = datetime.timedelta(30)
                    else:
                        td = datetime.timedelta(60)
                    today = datetime.date.today()
                    if (eventDate >= today and eventDate < today+td):
                        termine.append(Termin(
                                match.group(1), match.group(3), match.group(4)));
                except:
                    Log.trace(Log.APP, "Termin kaputt: "+line)
                    pass
    termineBereit = 0

def load_termine():
    global termineStr
    global termineBereit
    try:
        print "Termine werden gelesen."
        file = urllib2.urlopen("http://coredump.c-base.org/coredump/TerMine?action=raw")
        print "Termine fertig gelesen."
        termineStr = file.read()
        termineBereit = 1
    except IOError, e:
        Log.trace(Log.APP, "Can't read Termine: "+str(e.reason))

exiting = 0
termineBereit = 0

def termin_watcher():
    global exiting
    while not(exiting):
        time.sleep(10)
        load_termine()
 
curInfoIndex = -1
 
def start_termin():
    global curTerminNum
    global terminVonLinks
    global termine
    global curInfoIndex
    if termine != [] :
        curInfoIndex += 1
        if curInfoIndex == len(termine):
            curInfoIndex = 0
        curInfo = termine[curInfoIndex]
        curTermin = Player.getElementByID("linie"+str(curTerminNum))
        topLine = Player.getElementByID("linie"+str(curTerminNum)+"_top")
        topLine.text = curInfo.event
        bottomLine = Player.getElementByID("linie"+str(curTerminNum)+"_bottom")
        bottomLine.text = curInfo.date+", "+curInfo.time
        if terminVonLinks:
            anim.SplineAnim(curTermin, "x", 1000, -800, 2000, 10, -20, 1,
                    lambda: anim.SplineAnim(curTermin, "x", 400, 10, -20, 0, 0, 1, None))
        else:
            anim.SplineAnim(curTermin, "x", 1000, 800, -2000, -10, 20, 1,
                    lambda: anim.SplineAnim(curTermin, "x", 400, -10, 20, 0, 0, 1, None))
        Player.setTimeout(3000, termin_weg)
    else:
        Player.setTimeout(3000, start_termin)
    if termineBereit:
        parse_termine()

def termin_weg():
    global curTerminNum
    global terminVonLinks
    curTerminNum += 1
    if curTerminNum == 4:
        curTerminNum = 1
    terminVonLinks = (random.random() > 0.5)
    curTermin = Player.getElementByID("linie"+str(curTerminNum))
    if terminVonLinks:
        anim.SplineAnim(curTermin, "x", 1000, 0, 0, 800, -2000, 1, None)
    else:
        anim.SplineAnim(curTermin, "x", 1400, 0, 0, -1200, 2000, 1, None)
    Player.setTimeout(1500, start_termin)


def init_termine():
    global curTerminNum
    global terminVonLinks
    socket.setdefaulttimeout(20)
    load_termine()
    Player.getElementByID("linie1").x=900
    Player.getElementByID("linie2").x=900
    Player.getElementByID("linie3").x=900
    curTerminNum = 1
    terminVonLinks = 0 
    Player.setTimeout(10, start_termin)
    thread.start_new_thread(termin_watcher, ())

class Ad:
    def __init__(self, name, index, start_date, end_date, init_func):
        self.name = name
        self.index = index
        self.start_date = start_date
        self.end_date = end_date
        self.init_func = init_func

class starsoda_ad:
    def __init__(self):
        self.__curFrame=0
        self.__stern = Player.getElementByID("starsoda_stern")
        self.__flasche = Player.getElementByID("starsoda_flasche")
        self.__starsoda = Player.getElementByID("starsoda_starsoda")
        self.__taste = Player.getElementByID("starsoda_taste_of_time")
        anim.LinearAnim(self.__flasche, "x", 6600, -240, 765, 0, None)
        Player.setTimeout(1200, lambda: setattr(self.__stern, "opacity", 0))
        Player.setTimeout(1900, lambda: setattr(self.__stern, "opacity", 1))
        Player.setTimeout(4700, lambda: setattr(self.__starsoda, "opacity", 1))
        Player.setTimeout(4700, 
                lambda: anim.LinearAnim(self.__starsoda, "x", 
                        5700, 351.0, 671.0, 0, None))
        Player.setTimeout(5000, lambda: setattr(self.__taste, "opacity", 1))
        Player.setTimeout(5000, 
                lambda: anim.LinearAnim(self.__taste, "x", 
                        1700, 196, 316, 0, None))
        Player.setTimeout(6300, lambda: anim.fadeOut(self.__taste, 400))
        Player.setTimeout(6350, lambda: anim.fadeOut(self.__starsoda, 400))
        Player.setTimeout(6700, self.__stop)
    def __stop(self):
        anim.fadeOut(Player.getElementByID("werbung"), 500) 
        Player.setTimeout(4000, init_werbung)

class cwars_ad:
    def __start_logo(self): 
        Player.getElementByID("c-wars").opacity = 1
        anim.fadeOut(Player.getElementByID("c-wars"), 3000)
        anim.LinearAnim(Player.getElementByID("c-wars"), 
                "x", 5000, 66, 40, 0, None) 
        anim.LinearAnim(Player.getElementByID("moon"), 
                "opacity", 300, 0.0, 1.0, 0, None)
    def __start_words1(self): 
        anim.LinearAnim(Player.getElementByID("where_past"), 
                "opacity", 2000, 1.0, 0.0, 0, None)
    def __start_words2(self):
        anim.LinearAnim(Player.getElementByID("meets_future"), 
                "opacity", 2000, 1.0, 0.0, 0, None)
    def __start_url(self): 
        Player.getElementByID("www_c-wars_com").opacity = 1
        anim.fadeOut(Player.getElementByID("www_c-wars_com"), 1500)
    def __stop(self): 
        anim.fadeOut(Player.getElementByID("werbung"), 500) 
        Player.getElementByID("trailer").opacity=0.0
        Player.getElementByID("trailer").stop()
        Player.getElementByID("moon").opacity = 1
        anim.fadeOut(Player.getElementByID("moon"), 500)
        Player.setTimeout(4000, init_werbung)
    def __init__(self):
        node = Player.getElementByID("trailer")
        node.play()
        node.opacity=1
        Player.setTimeout(2000, self.__start_logo)
        Player.setTimeout(3000, self.__start_words1)
        Player.setTimeout(4500, self.__start_words2)
        Player.setTimeout(6000, self.__start_url)
        Player.setTimeout(8500, self.__stop)
        
class puppets_ad:
    def __init__(self):
        self.__puppets = Player.getElementByID("puppets")
        self.__logo = Player.getElementByID("puppets_logo")
#        self.__intervalID=Player.setInterval(10, self.__move)
        Player.getElementByID("puppets").opacity=0
        Player.getElementByID("puppets").x=360
        Player.getElementByID("puppets_logo").opacity=0
        Player.setTimeout(1000, self.__startJumps)
        Player.setTimeout(2000, self.__showLogo)
        Player.setTimeout(5500, self.__hideLogo)
        Player.setTimeout(6000, self.__hidePuppets)
        Player.setTimeout(6100, self.__showPuppets)
        Player.setTimeout(6250, self.__hidePuppets)
        Player.setTimeout(6350, self.__showPuppets)
        Player.setTimeout(6800, self.__stop)
        self.__curTextIndex=0
    def __startJumps(self):
        self.__puppets.opacity = 1
        self.__jumpCount = 0
        self.__startJump()
        anim.LinearAnim(self.__puppets, "x", 2100, 
                self.__puppets.x, self.__puppets.x+120, 0, None)
    def __startJump(self):
        self.__jumpCount+=1
        if self.__jumpCount < 4:
            anim.SplineAnim(self.__puppets, "y", 350, 5, -55, 10, 0, 0, self.__startFall)
    def __startFall(self):
        anim.SplineAnim(self.__puppets, "y", 350, -55, 5, 0, 10, 0, self.__startJump)
    def __showPuppets(self):
        self.__puppets.opacity = 1
    def __showLogo(self):
        self.__logo.opacity = 1
    def __hidePuppets(self):
        self.__puppets.opacity = 0
    def __hideLogo(self):
        self.__logo.opacity = 0
    def __stop(self):
        anim.fadeOut(Player.getElementByID("werbung"), 500) 
        Player.setTimeout(4000, init_werbung)

#def godzilla_appears() {
#    var godzilla=Player.getElementByID("godzilla");
#    godzilla.opacity=1;
#    animateFloatAttr("godzilla_group", "y", 200, 4, 600); 
#}

#def godzilla_shoots() {
#    var eyes=Player.getElementByID("eyes");
#    eyes.opacity=1;
#    var rays=Player.getElementByID("rays");
#    rays.opacity=1;
#    rays.angle=10;
#    rays.pivotx=378;
#    animateFloatAttr("rays", "angle", 10, 0, 300);
#}

#def show_title() {
#    var title=Player.getElementByID("title");
#    title.opacity=1;
#}

#def show_date() {
#    var title=Player.getElementByID("title");
#    title.opacity=0;
#    var date=Player.getElementByID("date");
#    date.opacity=1;
#}

#def fadeout() {
#    animateFloatAttr("city", "opacity", 1, 0, 300); 
#    animateFloatAttr("godzilla", "opacity", 1, 0, 300); 
#    animateFloatAttr("eyes", "opacity", 1, 0, 300); 
#    animateFloatAttr("rays", "opacity", 1, 0, 300); 
#    animateFloatAttr("date", "opacity", 1, 0, 1500); 
#}

#def init_mingle() {
#    print("init_mingle");
#    Player.getElementByID("werbung_switch").activechild=1;
#    animateFloatAttr("city", "opacity", 0, 1, 400);
#    animateFloatAttr("city", "x", 0, -250, 5000);
#    var godzilla_group=Player.getElementByID("godzilla_group");
#    godzilla_group.y=200;
#    Player.setTimeout(1000, "godzilla_appears()");
#    Player.setTimeout(2500, "godzilla_shoots()");
#    Player.setTimeout(3200, "show_title()");
#    Player.setTimeout(5000, "show_date()");
#    Player.setTimeout(5500, "fadeout()");
#    Player.setTimeout(8500, "init_werbung();");
#    Player.getElementByID("godzilla").opacity=0;
#    Player.getElementByID("eyes").opacity=0;
#    Player.getElementByID("rays").opacity=0;
#    Player.getElementByID("title").opacity=0;
#    Player.getElementByID("date").opacity=0;
#    Player.getElementByID("werbung").opacity=1.0; 
#}

#def stop_phneutral()
#{
#    animateFloatAttr("ph_neutral_logo", "opacity", 1, 0, 500);       
#    Player.setTimeout(2000, "init_werbung();");
#}

#def init_phneutral()
#{
#  curFrame=0;
#  animateFloatAttr("ph_neutral_logo", "opacity", 0, 1, 500);       
#  Player.getElementByID("ph_neutral_logo").play();
#  Player.setTimeout(10000, "stop_phneutral()");
#//  intervalID=Player.setInterval(10,"move_starsoda();");
#}

#def gmove(id,speed):
#    node = Player.getElementByID(id)
#    node.opacity=1
#    node.x += speed
#    if node.x > Player.getElementByID("gimp_main").width:
#        node.x = -300
#    if node.x < -300:
#        node.x = Player.getElementByID("gimp_main").width

#def stopGimpAnimation():
#    global intervalID
#    Player.setTimeout(2000, init_werbung)
#    Player.getElementByID("werbung").opacity = 0.0
#    Player.clearInterval(intervalID)

#def startGimpAnimation():
#    global intervalID
#    intervalID= Player.setInterval(27, lambda: gmove('gimp_title',9))
#    Player.setTimeout(8500, stopGimpAnimation)

adSchedule= [
#              Ad("phneutral", 3, date(2004,4,16), date(2004,4,23), init_phneutral),
              Ad("starsoda", 0, datetime.date(2002,4,16), 
                    datetime.date(2014,4,23), starsoda_ad),
#              Ad("meet and mingle", 1, date(2004,2,1), date(2004,3,1), init_mingle),
              Ad("puppetmastaz", 2, datetime.date(2004,2,1), 
                    datetime.date(2014,3,1), puppets_ad),
#              Ad("gimp", 4, date(2004,2,1), date(2014,10,1), startGimpAnimation)
              Ad("c-wars", 5, datetime.date(2004,2,1), 
                    datetime.date(2014,10,1), cwars_ad)
            ]

def switch_to_ad(index):
    adsNode = Player.getElementByID("werbung_switch");
    for i in range(adsNode.getNumChildren()):
        if i == index:
            adsNode.getChild(i).active = True
        else:
            adsNode.getChild(i).active = False

curWerbung = 0

def init_werbung():
    global curWerbung
    global curAds
    curWerbung += 1
    curWerbung %= len(curAds)
    anim.fadeIn(Player.getElementByID("werbung"), 500, 1)
    switch_to_ad(curAds[curWerbung].index)
    curAds[curWerbung].init_func()

def init_cur_ads():
    global curAds
    print("Configured ads: ")
    curAds = []
    for curAd in adSchedule:
        print("startDate: " + str(curAd.start_date))
        print("endDate: " + str(curAd.end_date))
        if (curAd.start_date <= datetime.date.today() and 
                curAd.end_date >= datetime.date.today()):
            curAds.append(curAd)
            print("  "+curAd.name)


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
#                  Log.PROFILE_LATEFRAMES |
                  Log.CONFIG 
#                 Log.MEMORY  |
#                 Log.BLTS    |
#                  Log.EVENTS
                  )
Player.loadFile("monitor3.avg")
init_cur_ads()
init_termine()
anim.init(avg)
Player.setTimeout(100, init_werbung)
Player.getElementByID("bkgndvideo").opacity = 0.3
Player.getElementByID("bkgndvideo").play()
Player.setVBlankFramerate(2)
Player.play()
done = 1
