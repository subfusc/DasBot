#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
import IRCFonts
import json
import urllib2
import time
import re
import random

class Plugin():
        
    def __init__(self): pass

    def help(self, command, args, channel, **kwargs):
        if command == 't':
            msg = [(1, kwargs['from_nick'], "Sanntidsinfo fra trafikanten:")]
            msg.append((1, kwargs['from_nick'], "!t hvor [ant [min]]"))
            msg.append((1, kwargs['from_nick'], "«hvor» kan blant annet være følgende: sognsvann, ullevål, ringen, sentrum og trikk"))
            msg.append((1, kwargs['from_nick'], "NB! Etter rutetidsendringer har ting blitt hacket og lappet sammen. Pluginen bør skrives på nytt"))
            return msg
        if command == 'all':
            return [(1, kwargs['from_nick'], "TrafikantenBot: t")]

    def cmd(self, command, args, channel, **kwargs):
        if command == 't':
            if args == None:
                args = 'sentrum'
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
                    for i in svar[1:-2]:
                        s = s + i.encode('utf-8') + "|"
                    s = s + svar[-1].encode('utf-8') + "]"
            return [(0, channel, kwargs["from_nick"], s)]
            #self.notify(kwargs["from_nick"], self.trafikanten_k(kwargs['Message']))

    def listen(self, msg, channel, **kwargs):
        if re.search(r"\bbanen\b", msg.lower()):
            return [(0, channel, self.trafikanten('sentrum'))]
        elif re.search(r"\bsentrum\b", msg.lower()):
            return [(0, channel, self.trafikanten('sentrum'))]
#        if re.search(r"\bringen\b", msg.lower()):
#            return [(0, channel, self.trafikanten('ringen'))]
        if re.search(r"\bsognsvann\b", msg.lower()):
            return [(0, channel, self.trafikanten('sognsvann'))]

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
                'trikken': 'trikk', 
                'adamstuen': 'trikk', 
                'sognsvann': 'Sognsvann',
                'ringen': 'Ringenfire',
                'r': 'Ringenfire',
                'golia': 'Mortensrud',
                'godlia': 'Mortensrud',
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
        hvor = k[0]
        if k[0].lower() in steder:
            hvor = steder[k[0].lower()] 

        if len(msg) == 0:
            hvor = 1
        nar = -1
        ant = 2
        if len(k) > 1:
            try:
                ant = int(k[1])
            except ValueError:
                ant = 2
        if len(k) > 2:
            try:
                nar = int(k[2])
            except ValueError:
                nar = -1
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
        count = 1
        for avgang in avganger:
            tid = (int(datere.match(avgang['ExpectedDepartureTime']).group(1)) - nu-14)/60000
            print "::::::::::::::::::::::::::::\n", hvor
            print avgang['DestinationName']
            print tmp
            if avgang['DirectionName'] == '1' and hvor != 'Ringenfire' and avgang['DestinationName'].lower() == k[0].lower() and tid > nar:
                count += 1
                tmp.append(str(tid) + ' min')
            elif hvor == 'Ringenfire' and avgang['DirectionName'] == '2' and 'Ringen' == avgang['DestinationName'] and tid > nar:
                count += 1
                tmp.append(str(tid) + ' min')
            elif hvor == avgang['DestinationName'] and tid > nar:
                count += 1
                tmp.append(str(tid) + ' min ('+ avgang['DestinationName'] + ')')
            elif hvor == '1' and avgang['DirectionName'] == '1' and tid > nar:
                count += 1
                tmp.append(str(tid) + ' min ('+ avgang['DestinationName'] + ')')
            elif hvor == 'trikk' and avgang['DirectionName'] == '1' and tid > nar:
                count += 1
                tmp.append(str(tid) + ' min (#'+ avgang['LineRef'] + ')')
            elif hvor == '2' and avgang['DirectionName'] == '2' and tid > nar:
                count += 1
                tmp.append(str(tid) + ' min ('+ avgang['DestinationName'] + ')')
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
        
        if kommando == 'ullevaal':
            tmp = ""
            hvor = "Sognsvann"
            for avgang in avganger:
                if avgang['DirectionName'] == '2':
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

        else:
            tmp = ""
            for avgang in avganger:
                if avgang['DirectionName'] == '1' and avgang['DestinationName'] == kommando:
                    tid = (int(datere.match(avgang['ExpectedDepartureTime']).group(1)) - nu+15)/60000
                    if tmp != "":
                        tmp = tmp.format(hvor, tid)
                        return tmp
                    elif tid == 0:
                        tmp = random.choice(setninger_nu)
                    else:
                        tmp = random.choice(setninger_normal).format(hvor, tid)
                        return tmp

