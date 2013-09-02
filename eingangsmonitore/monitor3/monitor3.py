from libavg import avg, AVGApp
from libavg.avg import DivNode,ImageNode,VideoNode,WordsNode,RectNode

import random
import MonitorJSONRPC
from Queue import Empty
from libavg.anim import EaseInOutAnim

g_player = avg.Player.get()
g_log = avg.Logger.get()

# der content selbst bestimmt die laenge seines contents
# d.h. man kann ganze filme abspielen ohne das sich was aendert


# wenn ein alert passiert, content ausblenden
# wenn ein alert passiert, waehrend ein andere active ist, alten ausblende, neuen einblenden
class ContentViewer(DivNode):
    __activeContent = None # which is actuall played
    __oldContent = None # last played content
    __timeBetweenAd = 1300 # in [ms]
    __state = None # see self.state

    content = []
    alert = None
    # states
    NOTHING = 1
    PLAYING = 2

    def addContent(self, content):
        self.content.append(content)
        content.opacity = 0

    def removeContent(self, content):
        if self.__activeContent == content:
            self.stopContent()
        self.content.remove(content)

    def alert(self):
        if not self.alert == None:
            self.alert.abort()
            avg.fadeOut(200, self.alert)
        self.alert = newAlert
        self.alert.start(self.alertEnd)
        avg.fadeIn(200, self.alert)

    def alertEnd(self):
        self.nextContent()

    def stopContent(self):
        if self.__activeContent:
            self.__activeContent.abort()
            self.end(self.__activeContent)

    def timedOut(self):
        self.stopContent()

    def state(self, newState):
        if newState == self.NOTHING:
            g_player.setTimeout(self.__timeBetweenAd, self.nextContent)
        if newState == self.PLAYING:
            self.__activeContent.start(self.end)

    # choose nextContent
    def nextContent(self):
        newContent = self.__oldContent
        oldContent = self.__oldContent
        print 'content : %d %s' % (len(self.content), self.content)
        if(len(self.content) == 0):
            print 'nothing found'
            g_player.setTimeout(1000, self.nextContent)
        elif(len(self.content) == 1):
            print 'only one object'
            newContent = self.content[0]
        else:
            print 'random content: old %s : new %s ' % (oldContent, newContent)
            while newContent == oldContent:
                print '1content chosen %s ' % newContent
                newContent = random.choice(self.content)
                print '2content chosen %s ' % newContent
        self.__activeContent = newContent
        if newContent:
            self.state(self.PLAYING)
            avg.fadeIn(newContent, 600)

    def startContent(self, content):
        newContent = self.__oldContent
        oldContent = self.__oldContent
        newContent = content
        self.stopContent()
        self.__activeContent = newContent
        if newContent:
            print "starting %s" % newContent
            self.state(self.PLAYING)
            avg.fadeIn(newContent, 600)

    '''
    called by content if they are done
    '''
    def end(self, content):
        self.__oldContent = self.__activeContent
        self.__activeContent = None
        if self.__oldContent:
            avg.fadeOut(self.__oldContent, 600)
        self.state(self.NOTHING)

class Content(DivNode):
    name = ""
    _endCallback = None
    # called before this content gets closed or abort (e.g. in result of an alert)
    # need to be called from child class
    def abort(self):
        pass

    # called when started
    # need to be called from child class
    def start(self, callback):
        self._endCallback = callback
        g_player.setTimeout(2000, self.end)

    # called when this Content is done
    # need to be called from child class
    def end(self):
        self.abort()
        self._endCallback(self)

class TextContent(Content):
    __text = None
    def __init__(self, text1="", text2="", text3="", *args, **kwargs):
        super(TextContent, self).__init__(*args, **kwargs)
        self.__whie = ImageNode(parent=self, pos=(0, 0), size=(800,200), href="hinweise/kasten_60.png", opacity=0.6)
        self.__topText = WordsNode(parent=self, text=text1, font='arial', color="000000", pos=(30, 10), opacity=1, fontsize=40)
        self.__middleText = WordsNode(parent=self, text=text2, font='arial', color="000000", pos=(30, 80), opacity=1, fontsize=40)
        self.__bottomText = WordsNode(parent=self, text=text3, font='arial', color="000000", pos=(30, 140), opacity=1, fontsize=30)

class Msg(Content):
    __timerList = []
    __endCallback = None
    def __init__(self, type, user, callback=None, *args, **kwargs):
        super(Msg, self).__init__(*args, **kwargs)
        self._video = VideoNode(parent=self, href="werbung/c-wars/c-wars-trailer.mpg", size=(800,200))
        if type == "login":
            self._logo = TextContent(opacity=1, parent=self, text1="Hallo %s," % user, text2="willkommen auf der c-base!", text3="")
        elif type == "logout":
            self._logo = TextContent(opacity=1, parent=self, text1="", text2="Bis bald %s!" % user, text3="")
        elif type == "message":
            self._logo = TextContent(opacity=1, parent=self, text1="", text2=user, text3="")
        else:
            self._logo = TextContent(opacity=1, parent=self, text1="irgendwas" % user, text2="ist", text3="kaputt")
        self._endCallback = callback

    def __start_logo(self):
        self._logo.opacity = 1
        avg.fadeOut(self._logo, 5000)

    def __last_step(self):
        self._video.pause()

    def abort(self):
        self._video.stop()
        for timer in self.__timerList:
            g_player.clearInterval(timer)
        if self._endCallback:
            self._endCallback(self)
        else:
            print 'no callback defined'
        super(Msg, self).abort()

    def reset(self):
        self._logo.opcatity = 0

    def start(self, callback):
        self._endCallback = callback
        self.reset()
        self._video.stop()
        #self._video.play()
        #self._video.opacity = 1
        self._video.opacity = 0
        self.__timerList.append(g_player.setTimeout(500, self.__start_logo))
        self.__timerList.append(g_player.setTimeout(6500, self.__last_step))
        self.__timerList.append(g_player.setTimeout(9500, self.end))

    # called by end
    def end(self):
        for timer in self.__timerList:
            g_player.clearInterval(timer)
        if self._endCallback:
            self._endCallback(self)
        else:
            print 'no callback defined'

class Message(Content):
    __timerList = []
    __endCallback = None
    def __init__(self, text, callback=None, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self._video = VideoNode(parent=self, href="werbung/c-wars/c-wars-trailer.mpg", size=(800,200))
        lines = text.split("\n")
        while len(lines) < 3: lines.append("")
        self._logo = TextContent(opacity=1, parent=self, text1=lines[0], text2=lines[1], text3=lines[2])
        self._endCallback = callback

    def __start_logo(self):
        self._logo.opacity = 1
        avg.fadeOut(self._logo, 5000)

    def __last_step(self):
        self._video.pause()

    def abort(self):
        self._video.stop()
        for timer in self.__timerList:
            g_player.clearInterval(timer)
        if self._endCallback:
            self._endCallback(self)
        else:
            print 'no callback defined'
        super(Msg, self).abort()

    def reset(self):
        self._logo.opcatity = 0

    def start(self, callback):
        self._endCallback = callback
        self.reset()
        self._video.stop()
        #self._video.play()
        #self._video.opacity = 1
        self._video.opacity = 0
        self.__timerList.append(g_player.setTimeout(500, self.__start_logo))
        self.__timerList.append(g_player.setTimeout(6500, self.__last_step))
        self.__timerList.append(g_player.setTimeout(9500, self.end))

    # called by end
    def end(self):
        for timer in self.__timerList:
            g_player.clearInterval(timer)
        if self._endCallback:
            self._endCallback(self)
        else:
            print 'no callback defined'

class CWars(Content):
    __timerList = []
    __endCallback = None
    def __init__(self, callback=None, *args, **kwargs):
        super(CWars, self).__init__(*args, **kwargs)
        self._video = VideoNode(parent=self, href="werbung/c-wars/c-wars-trailer.mpg", size=(800,200))
        self._logo = ImageNode(parent=self, href="werbung/c-wars/c-wars.tif", pos=(66, 58))
        self._endCallback = callback
        self.__where_past = ImageNode(parent=self, href="werbung/c-wars/where_past.tif", pos=(48, 148))
        self.__meets_future = ImageNode(parent=self, href="werbung/c-wars/meets_future.tif", pos=(248, 148))
        self.__www_cwars_com = ImageNode(parent=self, href="werbung/c-wars/www_c-wars_com.tif", pos=(470, 152))

    def __start_logo(self):
        self._logo.opacity = 1
        avg.fadeOut(self._logo, 2000)

    def __start_where_past(self):
        avg.fadeIn(self.__where_past, 1000)

    def __start_meets_future(self):
        # anim.LinearAnim(Player.getElementByID("meets_future"), 
        # "opacity", 2000, 1.0, 0.0, 0, None)
        avg.fadeIn(self.__meets_future, 1000)

    def __start_url(self):
        avg.fadeIn(self.__www_cwars_com, 1000)

    def __last_step(self):
        self._video.pause()

    def abort(self):
        self._video.stop()
        for timer in self.__timerList:
            g_player.clearInterval(timer)
        if self._endCallback:
            self._endCallback(self)
        else:
            print 'no callback defined'
        super(CWars, self).abort()

    def reset(self):
        self._logo.opcatity = 0
        self.__where_past.opacity = 0
        self.__www_cwars_com.opacity = 0
        self.__meets_future.opacity = 0

    def start(self, callback):
        self._endCallback = callback
        self.reset()
        self._video.stop()
        self._video.play()
        self._video.opacity = 1
        self.__timerList.append(g_player.setTimeout(2000, self.__start_logo))
        self.__timerList.append(g_player.setTimeout(3000, self.__start_where_past))
        self.__timerList.append(g_player.setTimeout(4500, self.__start_meets_future))
        self.__timerList.append(g_player.setTimeout(6000, self.__start_url))
        self.__timerList.append(g_player.setTimeout(6500, self.__last_step))
        self.__timerList.append(g_player.setTimeout(9500, self.end))

    # called by end
    def end(self):
        for timer in self.__timerList:
            g_player.clearInterval(timer)
        if self._endCallback:
            self._endCallback(self)
        else:
            print 'no callback defined'

class StaticWerbung:
    def __init__(self, top=None, bottom=None):
        self._top = top
        self._bottom = bottom
        self._list = []

        cwars = CWars
        self._list.append(cwars)

    def next(self):
        pass

class MonitorMain(DivNode):
    def __init__(self, *args, **kwargs):
        super(MonitorMain, self).__init__(*args, **kwargs)
        # basic overlay
        self.overlay = DivNode(parent=self)
        self.video = VideoNode(href="base_loop.avi", loop=True, parent=self.overlay, size=(800, 600))
        self.video.play()
        self.topDiv = DivNode(parent=self.overlay, pos=(0, 62), size=(800,200))
        self.bottomDiv = DivNode(parent=self.overlay, pos=(0, 363), size=(800, 200))
        ImageNode(href="rillen_70.png", parent=self.bottomDiv, size=(800,300))
        ImageNode(href="rillen_70.png", parent=self.topDiv, size=(800,300))
        ImageNode(href="schwarze_maske.png", parent=self.overlay)

        # top
        self.top = ContentViewer(parent=self.topDiv)

        # bottom
        self.bottom = ContentViewer(parent=self.bottomDiv)
        self._cwars = CWars(opacity=0, parent=self.bottom)
        self.bottom.addContent(self._cwars)
        print "running MonitorMain"
        g_log.trace(g_log.ERROR, "running monitormain now")
        self.bottom.nextContent()

    def login(self, user):
        #message = Msg("login", user, opacity=0, parent=self.bottom)
        message = Message("Hallo %s,\nwillkommen auf der c-base!" % user, opacity=0, parent=self.bottom)
        self.bottom.startContent(message)
        return 

    def logout(self, user):
        message = Msg("logout", user, opacity=0, parent=self.bottom)
        self.bottom.startContent(message)
        return 

    def message(self, message):
        msg = Msg("message", message, opacity=0, parent=self.bottom)
        self.bottom.startContent(msg)
        return 

class Monitor3(AVGApp):
    def init(self):
        self.jsonrpcserver, self.rpcqueue = MonitorJSONRPC.forkServer(port=9090)
        self.scheduler = g_player.setInterval(500, self.handle_jsonrpc)
        self.content = MonitorMain(mediadir="media/", size=g_player.getRootNode().size, parent=self._parentNode)

    def handle_jsonrpc(self):
        try:
            event = self.rpcqueue.get(False)
            # process event
            user = event[1]
            timestamp = event[2]
            if event[0] == "login":
                self.content.login(user) 
            elif event[0] == "logout":
                self.content.logout(user)
            elif event[0] == "message":
                self.content.message(user)
            else:
                # unknown event, do nothing
                pass
            
        except Empty: pass

if __name__ == '__main__':
    Monitor3.start(resolution=(800, 600))
