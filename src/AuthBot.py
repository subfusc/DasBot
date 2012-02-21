# -*- coding: utf-8 -*-

import IRCbot
import AuthSys
from GlobalConfig import *

class AuthBot(IRCbot.IRCbot):
    """
    This is a class where the IRCBot has an authentication system
    TODO: Use existing authentication mekanism
    """

    def __init__(self, host, port, nick, ident, realname):
        super(AuthBot, self).__init__(host, port, nick, ident, realname)
<<<<<<< HEAD
#        secret = raw_input('SECRET:')
#        self.authsys = AuthSys.AuthSys(secret)
=======

        if AUTHENTICATION:
            secret = raw_input('SECRET:')
            self.authsys = AuthSys.AuthSys(secret)
>>>>>>> 4546eb727176901b0051afca650b8e984a19230b
        
    def cmd(self, command, args, channel, **kwargs):
        super(AuthBot, self).cmd(command, args, channel, **kwargs)

        if AUTHENTICATION:
            if command == 'register':
                args = args.split()
                result = self.authsys.add(args[0], args[1])
                if result: self.msg(channel, result, to=kwargs['from_nick'])
                else: self.msg(channel, "Email sendt to %s" % (args[1]), to=kwargs['from_nick'])
            
    def listen(self, command, msg, channel, **kwargs):
        super(AuthBot, self).listen(command, msg, channel, **kwargs)

    def management_cmd(self, command, args, **kwargs):
        super(AuthBot, self).management_cmd(command, args, **kwargs)
    
if __name__ == "__main__":
    HOST='irc.ifi.uio.no' #The server we want to connect to 
    PORT=6667 #The connection port which is usually 6667 
    NICK='Subot' #The bot's nickname 
    IDENT='Subot' 
    REALNAME='Aweseome Bot' 
    OWNER='Subfusc' #The bot owner's nick 
    
    bot = AuthBot(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join("#nybrummbot")
    bot.notify("#nybrummbot", "HAI PEEPS!")
    bot.msg("#nybrummbot", "Example for you bro!", to="emanuel")
    bot.start()
