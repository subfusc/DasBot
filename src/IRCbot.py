# -*- coding: utf-8 -*-

import sys 
import socket 
import string 
import re
import traceback
from GlobalConfig import *

IDENT_RE = r'^:(?P<nick>[^!]+)![~^](?P<ident>[^@]+)@(?P<hostmask>.+)\s*$'

class IRCbot(object):

    def __init__(self, host, port, nick, ident, realname):
        self.host = host #: The IP/URL for the server
        self.port = port #: The port number for the server 
        self.nick = nick #: The nick the bot is going to use
        self.ident = ident #: Identity of the bot
        self.realname = realname #: The "realname" of the bot
        self.s = socket.socket() #: Create a socket for the I/O to the server
        self.channel = {} #: Channels we are in
        self.ident_re = re.compile(IDENT_RE) #: Extract information from the identity string

    def connect(self):
        self.s.connect((self.host, self.port)) #Connect to server 
        self.s.send('NICK ' + self.nick + '\n') #Send the nick to server 
        self.s.send('USER ' + self.ident + ' ' + self.host + ' SB: ' + self.realname + '\n') #Identify to server

        while 1: # Join loop 
            line = self.s.recv(1024) #recieve server messages 
            print line #server message is output 
            line = line.rstrip() #remove trailing 'rn' 
            line = line.split() 

            if '376' in line:
                print "End MOTD found!"
                break
            
            # if line[3].find(':\x01VERSION\x01') != -1 or line[3].find(':VERSION')  != -1: #This is Crap 
            #     print "Presumably connected"
            #     self.msg(line[0][1:], '\x01VERSION 0.0.0.0.0.0.1\x01\n')
            #     break
            
            if len(line) > 1 and line[0] == 'PING': #If server pings then pong 
                if VERBOSE: print "replying to pong \'%s\'" % ('PONG ' + line[1])
                self.s.send('PONG ' + line[1] + '\n')  
        
        return True
    
    def join(self, name):
        if not name in self.channel:
            self.channel[name] = []
            self.s.send('JOIN ' + name + '\n');
            line = self.s.recv(1024)
            line = line.rstrip()
            line = line.split("353")
            if len(line) >= 2:
                line = line[1].split(":")
                nicks = line[1]
                
                nicks = nicks.split()
                for nick in nicks:
                    if nick[0] == "+" or nick[0] == "@":
                        self.channel[name].append(nick[1:])
                    else:
                        self.channel[name].append(nick)
                        
                return "I Joined " + name + ", and ready to spy on: " + ", ".join(self.channel[name])
            else:
                del self.channel[name]
                return "DID NOT JOIN! LULZ!"

        else:
            return "Allready in channel"

    def part(self, name):
        if name in self.channel:
            self.s.send('PART ' + name + '\n')
            del self.channel[name]
            return "PULLING OUUUUTTT!"
        else:
            return "Not in that channel"

    def msg(self, name, message, to = None):
        if name[0] == '#':
            if to: self.s.send("PRIVMSG " + name + " :" + to + ", " + message + "\n")
            else: self.s.send("PRIVMSG " + name + " :" + message + "\n")
        elif to != None:
            self.s.send("PRIVMSG " + to + " :" + message + "\n")

    def private_msg(self, to, message):
        self.s.send("PRIVMSG %s :%s\n" % (to, message))
            
    def notify(self, name, message):
        self.s.send("NOTICE " + name + " :" + message + "\n")

    def _parse_raw_input(self, line):
        line = line.rstrip()
        line = line.split()

        if DEBUG: print(line)
        if len(line) == 2:
            self._server_command(line[0], line[1][1:])
            return

        match = self.ident_re.match(line[0])
        try:
            line[3] = line[3][1:]
            if line[3][0] == '!':
                line[3] = line[3][1:]
                
                self.cmd(line[3], 
                         " ".join(line[4:]) if len(line) > 4 else None, 
                         line[2],
                         from_nick = match.group('nick'),
                         from_ident = match.group('ident'),
                         from_host_mask = match.group('hostmask'))
            
            self.listen(line[1], " ".join(line[3:]), line[2],
                        from_nick=match.group('nick'),
                        from_ident=match.group('ident'),
                        from_host_mask=match.group('hostmask'))
            
        except Exception as e:
            print "I got an error here: %s" % e
            traceback.print_tb(sys.exc_info()[2], limit=1, file=sys.stdout)
            
    def start(self):
        while 1: # Main Loop
            line = self.s.recv(1024) #recieve server messages

            if VERBOSE: print line #server message is output
            line = self._parse_raw_input(line)

    def _server_command(self, command, msg):
        """
        This command is for the network layer to respond to diffrent server
        requests, like ping.
        """
        
        if command == 'PING': #If server pings then pong 
            if VERBOSE: print "replying to pong \'%s\'" % ('PONG ' + msg)
            self.s.send('PONG ' + ":" + msg + '\n')

    def cmd(self, command, args, channel, **kwargs):
        """
        This function, when extended in your class, will give you all commands (as determined by
        the globalconf COMMAND_CHAR) written in a channel.
        If you are only going to run commands and not doing anything with NLP, please extend this
        to avoid unecessary overhead.
        """
        if VERBOSE:
            print(":COMMAND: Command: %s, Message: %s, Channel: %s, From: %s!%s@%s" % (command, args, 
                                                                                       channel,
                                                                                       kwargs["from_nick"], 
                                                                                       kwargs["from_ident"],
                                                                                       kwargs["from_host_mask"]))   
            
    def listen(self, command, msg, channel, **kwargs):
        """
        This Function is supposed to be extended in subclasses to provide functionality when you
        want all sentences, and not just commands. If you want only commands, please extend
        cmd.
        """
        if VERBOSE:
            print(":LISTEN: Command: %s, Message: %s, Channel: %s, From: %s!%s@%s" % (command, msg, 
                                                                                      channel,
                                                                                      kwargs["from_nick"], 
                                                                                      kwargs["from_ident"],
                                                                                      kwargs["from_host_mask"]))

if __name__ == "__main__":
    HOST='irc.ifi.uio.no' #The server we want to connect to 
    PORT=6667 #The connection port which is usually 6667 
    NICK='Automott' #The bot's nickname 
    IDENT='automott' 
    REALNAME='Aweseome Bot' 
    OWNER='Trondth' #The bot owner's nick 
    
    bot = IRCbot(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join("#nybrummbot")
    bot.notify("#nybrummbot", "HAI PEEPS!")
    bot.msg("#nybrummbot", "Example for you bro!", to="emanuel")
    bot.start()
