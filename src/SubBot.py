#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Skrevet av Sindre Wetjen
import re

from IRCbot import IRCbot
from AuthSys import AuthSys

CMD_TOKEN = "."

class SubBot(IRCbot):

    def __init__(self, host, port, nick, ident, realname):
        IRCbot.__init__(self, host, port, nick, ident, realname)
        self.auth = AuthSys()
        self.cmdre = re.compile("^(\S+)(\s+(.*))?$")

    def cmd(self, domain, to, fro, cmd, message = None):
        print "Got cmd, match cmd: %s" % (cmd)
        
        if cmd == "login":
            message = message.split()
            if len(message) >= 2:
                self.auth.login(message[0], " ".join(message[1:]), domain)

        if cmd == "logout":
            self.auth.logout(domain)

        if cmd == "register":
            message = message.split()
            if len(message) >= 2:
                self.auth.add(message[0], " ".join(message[1:]))

        if self.auth.online(domain):
            if cmd == "notify":
                message = message.split()
                if len(message) == 2:
                    self.notify(message[0], message[1])
                elif len(message) > 2:
                    self.notify(message[0], " ".join(message[1:]))
                    
            if cmd == "say":
                message = message.split()            
                if len(message) == 2:
                    self.msg(message[0], message[1])
                elif len(message) > 2:
                    self.msg(message[0], " ".join(message[1:]))
                    
            if cmd == "join":
                if message:
                    self.msg(fro, self.join(message), to)

            if cmd == "part":
                if message:
                    self.msg(fro, self.part(message), to)
        

            if self.auth.level(domain) == "a":
                if cmd == "list":
                    self.msg(fro, self.auth.list_users(), to)

        

    def channel_message(self, channel, nick, domain, message):
        if message[0] == CMD_TOKEN:
            match = self.cmdre.match(message)
            self.cmd(domain, nick, channel, match.group(1)[1:], match.group(3))


    def private_message(self, nick, domain, message):
        if message[0] == CMD_TOKEN:
            match = self.cmdre.match(message)
            self.cmd(domain, None, nick, match.group(1)[1:], match.group(2))
            
    def quit(self, line):
        nick, domain = line[0].split("!")
        nick = nick[1:]
        print "logging out %s %s" % (nick, domain)
        self.auth.logout(domain)

if __name__ == "__main__":
    HOST='ogn1.onlinegamesnet.net' #The server we want to connect to 
    PORT=6660 #The connection port which is usually 6667 
    NICK='PySub' #The bot's nickname 
    IDENT='pybot' 
    REALNAME='Aweseome Bot' 
    OWNER='Subfusc' #The bot owner's nick 
    
    bot = SubBot(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join("#eternalfaith")
    bot.listen()
