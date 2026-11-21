# intertwingle: a fancy name for some global variables so I don't have to do a proper architecturing

global config
global lewp
global comms
global hlog

global status_announce_playtest
global status_announce_centcom

def setComms(proc):
    global comms
    comms = proc

def getComms():
    global comms
    return comms

def setConfig(conf):
    global config
    config = conf

def getConfig():
    global config
    return config

def setLoop(loop):
    global lewp
    lewp = loop

def getLoop():
    global lewp
    return lewp

def setLogger(logger):
    global hlog
    hlog = logger

def getLogger():
    global hlog
    return hlog

def resetAnnounceFlags():
    global status_announce_playtest
    global status_announce_centcom
    status_announce_playtest = True
    status_announce_centcom = True
