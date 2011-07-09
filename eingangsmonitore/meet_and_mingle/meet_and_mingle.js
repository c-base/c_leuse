
use("../../libavg/src/avg.js");
use("../common.js");


function godzilla_appears() {
    var godzilla=AVGPlayer.getElementByID("godzilla");
    godzilla.opacity=1;
    animateFloatAttr("godzilla_group", "y", 241, 4, 1000); 
}

function godzilla_shoots() {
    var eyes=AVGPlayer.getElementByID("eyes");
    eyes.opacity=1;
    var rays=AVGPlayer.getElementByID("rays");
    rays.opacity=1;
    rays.angle=10;
    rays.pivotx=378;
    animateFloatAttr("rays", "angle", 10, 0, 500);
}

function show_title() {
    var title=AVGPlayer.getElementByID("title");
    title.opacity=1;
}

function show_date() {
    var title=AVGPlayer.getElementByID("title");
    title.opacity=0;
    var date=AVGPlayer.getElementByID("date");
    date.opacity=1;
}

function fadeout() {
    animateFloatAttr("city", "opacity", 1, 0, 500); 
    animateFloatAttr("godzilla", "opacity", 1, 0, 500); 
    animateFloatAttr("eyes", "opacity", 1, 0, 500); 
    animateFloatAttr("rays", "opacity", 1, 0, 500); 
    animateFloatAttr("date", "opacity", 1, 0, 2500); 
     
}

function meet_and_mingle_ad() {
    animateFloatAttr("city", "opacity", 0, 1, 400);
    animateFloatAttr("city", "x", 0, -250, 5000);
    var godzilla_group=AVGPlayer.getElementByID("godzilla_group");
    godzilla_group.y=241;
    AVGPlayer.setTimeout(1000, "godzilla_appears()");
    AVGPlayer.setTimeout(2500, "godzilla_shoots()");
    AVGPlayer.setTimeout(3200, "show_title()");
    AVGPlayer.setTimeout(5000, "show_date()");
    AVGPlayer.setTimeout(5500, "fadeout()");
    AVGPlayer.getElementByID("godzilla").opacity=0;
    AVGPlayer.getElementByID("eyes").opacity=0;
    AVGPlayer.getElementByID("rays").opacity=0;
    AVGPlayer.getElementByID("title").opacity=0;
    AVGPlayer.getElementByID("date").opacity=0;
}

var ok = AVGPlayer.loadFile("meet_and_mingle.avg");
if (!ok) {
    print ("js: AVGPlayer.loadFile returned false");
}
AVGPlayer.setDebugOutput(AVGPlayer.DEBUG_PROFILE | 
		AVGPlayer.DEBUG_MEMORY);

AVGPlayer.setTimeout(10, "meet_and_mingle_ad();");
AVGPlayer.setInterval(9000, "meet_and_mingle_ad();");
AVGPlayer.play(25);

