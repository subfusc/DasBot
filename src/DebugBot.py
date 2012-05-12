# -*- coding: utf-8 -*-
import AuthBot
import time
import threading
from GlobalConfig import *

class DebugBot(AuthBot.AuthBot):
        
    def __init__(self, host, port, nick, ident, realname):
        super(DebugBot, self).__init__(host, port, nick, ident, realname)

    def cmd(self, command, args, channel, **kwargs):
        super(DebugBot, self).cmd(command, args, channel, **kwargs)
        if DEBUG or VERBOSE:
            if command == "whos":
                self.msg(channel, str(self.channel[channel][args]) if args in self.channel[channel] else "Not legal key", to=kwargs['from_nick'])
                
    def listen(self, command, msg, channel, **kwargs):
        super(DebugBot, self).listen(command, msg, channel, **kwargs)

    def help(self, command, args, channel, **kwargs):
        super(DebugBot, self).help(command, args, channel, **kwargs)
        if DEBUG or VERBOSE:
            if command == "whos":
                self.notify(kwargs["from_nick"], 
                            "!whos [op|voice|user] will give a list of all the people the bot thinks are $OPT.")
            elif command == "all":
                self.notify(kwargs["from_nick"],
                            "DebugBot: whos")
                
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
