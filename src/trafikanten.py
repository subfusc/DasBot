#!/usr/bin/python
# -*- coding: utf-8 -*-

import IRCbot
from GlobalConfig import *
import json
import urllib2
import time
import re
import random

class Shepard(IRCbot.IRCbot):
        
    def __init__(self, host, port, nick, ident, realname):
        super(Shepard, self).__init__(host, port, nick, ident, realname)

    def cmd(self, command, args, channel, **kwargs):
        super(Shepard, self).cmd(command, args, channel, **kwargs)        
        if VERBOSE: print "COMMAND FISKERN!"
        if command == '!t':
            #self.msg(channel, self.trafikanten_k(args, **kwargs))
            self.notify(kwargs["from_nick"], self.trafikanten_k(args))

    def listen(self, command, msg, channel, **kwargs):
        super(Shepard, self).listen(command, msg, channel, **kwargs)
        if VERBOSE: print "LISTEN mrShepard!"
        if msg.lower().find("banen") != -1:
            self.msg(channel, self.trafikanten('sentrum'))
        if msg.lower().find("ringen") != -1:
            self.msg(channel, self.trafikanten('ringen'))
        if msg.lower().find("sognsvann") != -1:
            self.msg(channel, self.trafikanten('sognsvann'))

    def trafikanten_realtime(self,hva):
        if hva != 'trikk':
            url = 'http://api-test.trafikanten.no/RealTime/GetRealTimeData/3010370'
            f = urllib2.urlopen(url)
            s = f.read()
            f.close()
        else:
            url = 'http://api-test.trafikanten.no/RealTime/GetRealTimeData/3010371'
            f = urllib2.urlopen(url)
            s = f.read()
            f.close()

    def trafikanten_k(self, kommando, args, **kwargs):
        stedet = {'sentrum': '1', 
                'trikk': 'trikk', 
                'Sognsvann': 'Sognsvann',
                'Murmansk': 'Sognsvann'}
        s = self.trafikanten_realtime(stedet[args[1]])
        datere = re.compile('^\/Date\(([^+]*)\+.*$')
        avganger = json.loads(s)
        """
        !t sentrum a=4 t=1040
        """
        if stedet['args[1]'] == 'sentrum':
            tmp = ""
            hvor = "sentrum"
            for avgang in avganger:
                if avgang['DirectionName'] == '1':
                    tid = (int(datere.match(avgang['ExpectedDepartureTime']).group(1)) - nu+15)/60000
                    if tmp != "":
                        tmp = tmp.format(hvor, tid)
                        return tmp
                    elif tid == 0:
                        tmp = random.choice(setninger_nu)
                    else:
                        tmp = random.choice(setninger_normal).format(hvor, tid)
                        return tmp
        

    def trafikanten(self, kommando):
        s = self.trafikanten_realtime(kommando)
        datere = re.compile('^\/Date\(([^+]*)\+.*$')
        avganger = json.loads(s)
        
        setninger_normal = ['Neste bane mot {0} går om {1} minutter',
'Du kommer deg til {0} om {1} minutter',
'Apropos {0}. Det er {1} minutter til banen går dit',
'Tralalalalabom. Tid minutter igjen til banen mot {0} går.',
'Visste du at banen til {0} går om {1} minutter?',
'Det er mye å si om {0}. Men vil du oppleve det personlig, kan du ta banen om {1} minutter.'
]
        setninger_normal_tr = ['Neste trikk går om {1} minutter']

        setninger_nu = ['Banen mot {0} går nå! Hvis du ikke vil løpe, går neste om {1} minutter',
]
        setninger_nu_tr = ['Trikken går nå! Hvis du ikke vil løpe, går neste om {1} minutter']

        setninger_trikk = ['Trikken går om {1} minutter.']
        
        nu = int(datere.match(avganger[0]['RecordedAtTime']).group(1))
        
        if kommando == 'sentrum':
            tmp = ""
            hvor = "sentrum"
            for avgang in avganger:
                if avgang['DirectionName'] == '1':
                    tid = (int(datere.match(avgang['ExpectedDepartureTime']).group(1)) - nu+15)/60000
                    if tmp != "":
                        tmp = tmp.format(hvor, tid)
                        return tmp
                    elif tid == 0:
                        tmp = random.choice(setninger_nu)
                    else:
                        tmp = random.choice(setninger_normal).format(hvor, tid)
                        return tmp
        
        if kommando == 'sognsvann':
            tmp = ""
            hvor = "Sognsvann"
            for avgang in avganger:
                if avgang['DestinationName'] == 'Sognsvann':
                    tid = (int(datere.match(avgang['ExpectedDepartureTime']).group(1)) - nu+15)/60000
                    if tmp != "":
                        tmp = tmp.format(hvor, tid)
                        return tmp
                    elif tid == 0:
                        tmp = random.choice(setninger_nu)
                    else:
                        tmp = random.choice(setninger_normal).format(hvor, tid)
                        return tmp
        
        if kommando == 'ringen':
            tmp = ""
            hvor = "Ringen"
            for avgang in avganger:
                if avgang['DestinationName'] == 'Ringen':
                    tid = (int(datere.match(avgang['ExpectedDepartureTime']).group(1)) - nu+15)/60000
                    if tmp != "":
                        tmp = tmp.format(hvor, tid)
                        return tmp
                    elif tid == 0:
                        tmp = random.choice(setninger_nu)
                    else:
                        tmp = random.choice(setninger_normal).format(hvor, tid)
                        return tmp

        if kommando == 'trikk':
            tmp = ""
            hvor = "nedover"
            for avgang in avganger:
                if avgang['DirectionName'] == '1':
                    tid = (int(datere.match(avgang['ExpectedDepartureTime']).group(1)) - nu+15)/60000
                    if tmp != "":
                        tmp = tmp.format(hvor, tid)
                        return tmp
                    elif tid == 0:
                        tmp = random.choice(setninger_nu_tr)
                    else:
                        tmp = random.choice(setninger_normal_tr).format(hvor, tid)
                        return tmp

if __name__ == "__main__":
    HOST='irc.ifi.uio.no' #The server we want to connect to 
    PORT=6667 #The connection port which is usually 6667 
    NICK='tralabot' #The bot's nickname 
    IDENT='tralalalalabot' 
    REALNAME='Tra La La' 
    OWNER='Trondth' #The bot owner's nick 
    
    bot = Shepard(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join("#nybrummbot")
    bot.notify("#nybrummbot", "tralalalalabom")
    #bot.msg("#nybrummbot", "Dæsken så mye fesk det e i fjorn i dag!")
    bot.start()


