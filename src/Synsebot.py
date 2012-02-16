# -*- coding: utf-8 -*-

import AuthBot
from GlobalConfig import *
#import nltk
import random
import re

class Synsebot(AuthBot.AuthBot):
    """
    This is a class where the IRCBot has an authentication system
    TODO: Use existing authentication mekanism
    """

    def __init__(self, host, port, nick, ident, realname):
        super(Synsebot, self).__init__(host, port, nick, ident, realname)

    def cmd(self, command, args, channel, **kwargs):
        super(Synsebot, self).cmd(command, args, channel, **kwargs)
        if command == 'm-add':
            self.mediekommentar-add(args)
        
    def listen(self, command, msg, channel, **kwargs):
        super(Synsebot, self).listen(command, msg, channel, **kwargs)
        medieord = re.compile(r'vg|dagbladet|db\.no|avisa|aftenposten|dagsavisen|dn\.no|klassekampen|pressen|pressa|ap\.no', re.IGNORECASE)
        print medieord.search(msg)
        if medieord.search(msg):
            self.msg(channel, self.mediekommentar(medieord.search(msg).group(0)))

    def mediekommentar-add(self, args):
        args = args.split()
        tag = args[0]
        sitat = args[1:]
        f = open('aviser.txt', 'a')
        f.write('\n\n')
        f.write('#' + tag + '\n')
        f.write(sitat)
        f.close()
        

    def mediekommentar(self, tag):
        alias = { 'db.no': 'dagbladet',
                'avisen': 'media',
                'pressen': 'media',
                'pressa': 'media',
                'ap.no': 'ap',
                'aftenposten': 'ap'
                }
        if tag in alias:
            tag = alias[tag]

        f = open('aviser.txt')
        tekst = f.read()
        tekst = tekst.split('\n\n')
        a = {}
        for e in tekst:
            tmp = re.sub("#(.*)\n", r"\g<1>###", e)
            tmp = tmp.split('###')
            if len(tmp) > 1:
                if not tmp[0] in a:
                    a[tmp[0]] = [tmp[1]]
                else:
                    a[tmp[0]].append(tmp[1])

        return random.choice(a[tag])


if __name__ == "__main__":
    HOST='irc.ifi.uio.no' #The server we want to connect to 
    PORT=6667 #The connection port which is usually 6667 
    NICK='Synsbot' #The bot's nickname 
    IDENT='Synsebot' 
    REALNAME='Synsebotten' 
    OWNER='Trondth' #The bot owner's nick 
    
    bot = Synsebot(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join("#nybrummbot")
#    bot.notify("#nybrummbot", "")
#    bot.msg("#nybrummbot", "Example for you bro!", to="emanuel")
    bot.start()
