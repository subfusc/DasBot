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
        if AUTHENTICATION:
            secret = raw_input('SECRET:')
            self.authsys = AuthSys.AuthSys(secret)
        
    def cmd(self, command, args, channel, **kwargs):
        super(AuthBot, self).cmd(command, args, channel, **kwargs)

        if AUTHENTICATION:
            if command == 'register':
                args = args.split()
                result = self.authsys.add(args[0], args[1])
                if result: self.msg(channel, result, to=kwargs['from_nick'])
                else: self.msg(channel, "Email sendt to %s" % (args[1]), to=kwargs['from_nick'])
            elif command == 'setpass':
                args = args.split()
                result = self.authsys.setpass(args[0], args[1], args[2])
                if result: self.msg(channel, "Password updated", to=kwargs['from_nick'])
                else: self.msg(channel, "Cookie not correct!", to=kwargs['from_nick'])
            elif command == 'login':
                args = args.split()
                result = self.authsys.login(args[0], args[1], "%s!%s@%s" % (kwargs['from_nick'],
                                                                            kwargs['from_ident'],
                                                                            kwargs['from_host_mask']))
                if result: self.msg(channel, "Logged in!", to=kwargs['from_nick'])
                else: self.msg(channel, "Wrong pass!", to=kwargs['from_nick'])
            elif command == 'online':
                result = self.authsys.is_online(args)
                if result: self.msg(channel, "He is online!", to=kwargs['from_nick'])
                else: self.msg(channel, "He is not online!", to=kwargs['from_nick'])
                
                
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
