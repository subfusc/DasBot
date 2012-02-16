#!/usr/bin/python
# -*- coding: utf-8 -*-

import AuthBot
from GlobalConfig import *
import codecs
import IRCFonts
import json
import urllib2
import time
import re
import random

class Shepard(AuthBot.AuthBot):
        
    def __init__(self, host, port, nick, ident, realname):
        super(Shepard, self).__init__(host, port, nick, ident, realname)

    def cmd(self, command, args, channel, **kwargs):
        super(Shepard, self).cmd(command, args, channel, **kwargs)        
        if VERBOSE: print "COMMAND mrShepard!"
        if command == 'help':
            if args.split()[0] == 't':
                self.notify(kwargs['from_nick'], "Sanntidsinfo fra trafikanten:")
                self.notify(kwargs['from_nick'], "!t hvor [min [ant]]")
                self.notify(kwargs['from_nick'], "«hvor» kan blant annet være følgende: sognsvann, ullevål, ringen, sentrum og trikk")

        if command == 't':
            svar = self.trafikanten_k(args)
            print "SVAR: ", svar
            if len(svar) < 2:
                s = "I am a Bear of Very Little Brain, and long words Bother me."
            else:
                print svar
                s1 = svar[0]
                print type(s1)
                print type(s1.decode('utf-8'))
                #print type(unicode(s1.decode('utf-8')))
                s2 = svar[1]
                s = s1 + s2.encode('utf-8')
                if len(svar) > 1:
                    s = s + " [neste "
                    for i in svar[2:-2]:
                        s = s + i.encode('utf-8') + "|"
                    s = s + svar[-1].encode('utf-8') + "]"
            self.msg(channel, s, to=kwargs["from_nick"])
            #self.notify(kwargs["from_nick"], self.trafikanten_k(kwargs['Message']))

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
        return s

    def trafikanten_k(self, msg):
        steder = {'sentrum': '1', 
                'trikk': 'trikk', 
                'adamstuen': 'trikk', 
                'sognsvann': 'Sognsvann',
                'ringen': 'Ringen',
                'byn': '1',
                'byen': '1',
                'jernbanetorget': '1',
                'oslo': '1',
                'nathionaltheatret': '1',
                'byen': '1',
                'ullevål': '2',
                'murmansk': 'Sognsvann'}
        k = msg.split()
        print ""
        datere = re.compile('^\/Date\(([^+]*)\+.*$')
        hvor = steder[k[0].lower()]
        nar = 0
        if len(k) > 1:
            nar = int(k[1])
        ant = 2
        if len(k) > 2:
            ant = int(k[2])
        s = self.trafikanten_realtime(hvor)
        avganger = json.loads(s)
        nu = int(datere.match(avganger[0]['RecordedAtTime']).group(1))
        """
        !t sentrum når antall
        """
        tmp = []
        if hvor != 'trikk':
            tmp.append("Avganger til %s: "  % k[0])
            print tmp
        else:
            tmp.append("Avganger med trikken: ")
            print tmp
        count = 0
        for avgang in avganger:
            tid = (int(datere.match(avgang['ExpectedDepartureTime']).group(1)) - nu-14)/60000
            print "::::::::::::::::::::::::::::\n", hvor
            print avgang['DestinationName']
            print tmp
            if avgang['DestinationName'] == hvor and tid > nar:
                count += 1
                tmp.append(str(tid))
            elif hvor == '1' and avgang['DirectionName'] == '1' and tid > nar:
                count += 1
                tmp.append(str(tid) + ' ('+ avgang['DestinationName'] + ')')
            elif hvor == 'trikk' and avgang['DirectionName'] == '1' and tid > nar:
                count += 1
                tmp.append(str(tid) + ' (#'+ avgang['LineRef'] + ')')
            elif hvor == '2' and avgang['DirectionName'] == '2' and tid > nar:
                count += 1
                tmp.append(str(tid) + ' ('+ avgang['DestinationName'] + ')')
            if count > ant:
                return tmp

        return tmp

    def trafikanten(self, kommando):
        s = self.trafikanten_realtime(kommando)
        datere = re.compile('^\/Date\(([^+]*)\+.*$')
        avganger = json.loads(s)
        
        setninger_normal = ['Neste bane mot {0} går om {1} minutter',
'Du kommer deg til {0} om {1} minutter',
'Apropos {0}. Det er {1} minutter til banen går dit',
'Tralalalalabom. {1} minutter igjen til banen mot {0} går.',
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


