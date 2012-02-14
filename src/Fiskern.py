# -*- coding: utf-8 -*-
import AuthBot
import time
from GlobalConfig import *

class Fiskern(AuthBot.AuthBot):
        
    def __init__(self, host, port, nick, ident, realname):
        super(Fiskern, self).__init__(host, port, nick, ident, realname)

    def cmd(self, command, args, channel, **kwargs):
        super(Fiskern, self).cmd(command, args, channel, **kwargs)        
        if VERBOSE: print "COMMAND FISKERN!"

        if command == "insult":
            self.msg(channel, "e du fette sprø i haue? æ ork da faen ikkje å ta mæ ti tel å lag sånnhærre tullekommandoa!", to=kwargs["from_nick"])
        elif command == "tell":
            self.private_msg(kwargs["from_nick"], "emanuel is lazy")
            
    def listen(self, command, msg, channel, **kwargs):
        super(Fiskern, self).listen(command, msg, channel, **kwargs)
        if VERBOSE: print "LISTEN FISKERN!"
        if msg.find("!insult") != -1:
            self.msg(channel, "please !insult %s" % (kwargs["from_nick"]))

if __name__ == "__main__":
    HOST='irc.ifi.uio.no' #The server we want to connect to 
    PORT=6667 #The connection port which is usually 6667 
    NICK='Fiskern' #The bot's nickname 
    IDENT='Fiskern' 
    REALNAME='Ola Nordlenning' 
    OWNER='Subfusc' #The bot owner's nick 
    
    bot = Fiskern(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join("#nybrummbot")
    bot.notify("#nybrummbot", "Ingenting e som å lig i fjorn å feske på en fin sommardag!")
    bot.msg("#nybrummbot", "Dæsken så mye fesk det e i fjorn i dag!")
    bot.start()
