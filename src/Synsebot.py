# -*- coding: utf-8 -*-
from GlobalConfig import *
import random
import re

DEBUG = False

class Plugin():
    """
    This is a class where the IRCBot has an authentication system
    TODO: Use existing authentication mekanism
    """

    avisertxt = 'aviser.txt'
    #print avisertxt

    def __init__(self):
        self.medieord = re.compile(r'\b(vg|dagbladet|db\.no|avisa|aftenposten|dagsavisen|dn\.no|klassekampen|pressen|pressa|ap\.no)\b', re.IGNORECASE)
        
    def cmd(self, command, args, channel, **kwargs):
        if command == 'm-add':
            if kwargs['auth_level'] >= 20:
                self.mediekommentaradd(args)
        
    def listen(self, msg, channel, **kwargs):
        if self.medieord.search(msg):
            return [(0, channel, self.mediekommentar(medieord.search(msg).group(0)))]

    def mediekommentaradd(self, args):
        args = args.split()
        tag = args[0]
        sitat = " ".join(args[1:])
        print sitat
        #print args
        f = open(Synsebot.avisertxt, 'a')
        #print Synsebot.avisertxt
        f.write('\n\n')
        f.write('#')
        f.write(tag)
        f.write('\n')
        f.write(sitat)
        f.close()
        

    def mediekommentar(self, tag):
        alias = { 'db.no': 'dagbladet',
                'avisen': 'media',
                'pressen': 'media',
                'pressa': 'media',
                'ap.no': 'ap',
                'aftenposten': 'ap',
                'dn.no': 'dn'
                }
        if tag in alias:
            tag = alias[tag]

        f = open(Synsebot.avisertxt)
        #print Synsebot.avisertxt
        tekst = f.read()
        tekst = re.sub('\n\n+', '\n\n', tekst)
        tekst = tekst.split('\n\n')
        #print tekst
        a = {}
        for e in tekst:
            tmp = re.sub("#([^#]*).*\n", r"\g<1>###", e)
            tmp = tmp.split('###')
            if len(tmp) > 1:
                if not tmp[0] in a:
                    a[tmp[0]] = [tmp[1]]
                else:
                    a[tmp[0]].append(tmp[1])

        return random.choice(a[tag.lower()])
