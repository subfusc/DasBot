# -*- coding: utf-8 -*-

import sys 
import socket 
import string 
import re
import traceback
from GlobalConfig import *

IDENT_RE = r'^:(?P<nick>[^!]+)![~^](?P<ident>[^@]+)@(?P<hostmask>\S+)'
CHANNEL_JOIN_RE = r':\S+\s353[^:]+:(?P<nicks>[^\n]+)'
MESSAGE_RE = r'^(?P<svcmd>[^!@\s]+)\s+:(?P<adress>[^!@]+(.[^!@\r\n])+)\s*$|' + IDENT_RE + r'\s+(?P<uscmd>\S+)\s+(?P<args>[^:\r\n]*)\s*(:(?P<msg>[^\r\n]+))?\s*$'

class IRCbot(object):

    def __init__(self, host, port, nick, ident, realname):
        self.host = host #: The IP/URL for the server
        self.port = port #: The port number for the server 
        self._nick = nick #: The nick the bot is going to use
        self.ident = ident #: Identity of the bot
        self.realname = realname #: The "realname" of the bot
        self.s = socket.socket() #: Create a socket for the I/O to the server
        self.channel = {} #: Channels we are in
        self.ident_re = re.compile(IDENT_RE) #: Extract information from the identity string
        self.channel_join_re = re.compile(CHANNEL_JOIN_RE)
        self.message_re = re.compile(MESSAGE_RE)
        
    def connect(self):
        self.s.connect((self.host, self.port)) #Connect to server 
        self.s.send('NICK ' + self._nick + '\n') #Send the nick to server 
        self.s.send('USER ' + self.ident + ' ' + self.host + ' SB: ' + self.realname + '\n') #Identify to server

        while 1: # Join loop 
            line = self.s.recv(1024) #recieve server messages 
            print line #server message is output 
            line = line.rstrip() #remove trailing 'rn' 
            line = line.split()

            if '376' in line:
                print "End MOTD found!"
                break
            
            if len(line) > 1 and line[0] == 'PING': #If server pings then pong 
                if VERBOSE: print "replying to pong \'%s\'" % ('PONG ' + line[1])
                self.s.send('PONG ' + line[1] + '\n')  
        
        return True
    
    def join(self, name):
        if not name in self.channel:
            self.channel[name] = {'op':[], 'voice':[], 'user':[]}
            self.s.send('JOIN ' + name + '\n');

            while True:
                line = self.s.recv(1024)
                if DEBUG: print line

                match = self.channel_join_re.search(line)
                if match:
                    nicks = match.group('nicks')
                    nicks = nicks.split()
                    for nick in nicks:
                        if nick[0] == "+":
                            self.channel[name]['voice'].append(nick[1:])
                        elif nick[0] == "@":
                            self.channel[name]['op'].append(nick[1:])
                        else:
                            self.channel[name]['user'].append(nick)
                    print self.channel[name]
                
                if line.find("366"): break
            
            return True
        else:
            return True

    def part(self, name):
        if name in self.channel:
            self.s.send('PART ' + name + '\n')
            del self.channel[name]
        return True

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

    def topic(self, channel, topic):
        self.s.send("TOPIC " + channel + " :" + topic + "\n")

    def nick(self, _nick):
        self.s.send("NICK " + _nick + "\n")
        self._nick = _nick
        
    def _parse_args(self, args, offset):
        length = len(args) + offset
        if length > 5 + offset:
            return " ".join(args[4 + offset:])
        elif length == 5 + offset:
            return args[4 + offset]
        else:
            return None 
        
    def _parse_raw_input(self, line):
        try:
            match = self.message_re.match(line)

            if DEBUG:
                print(match.groups())
                        
            if match.group('svcmd'):
                self._server_command(match.group('svcmd'), match.group('adress'))
                return

            if match.group('uscmd') == 'PRIVMSG':
                try:
                    if match.group('msg')[0] == '!':
                        first_space = match.group('msg').find(" ")
                        self.cmd(match.group('msg')[1:first_space] if first_space != -1 else match.group('msg')[1:],
                                 match.group('msg')[first_space + 1:] if first_space != -1 else None,
                                 match.group('args').strip(),
                                 from_nick=match.group('nick'),
                                 from_ident=match.group('ident'),
                                 from_host_mask=match.group('hostmask'))
                
                    else:
                        self.listen(match.group('uscmd'), match.group('msg'), match.group('args').strip(),
                                    from_nick=match.group('nick'),
                                    from_ident=match.group('ident'),
                                    from_host_mask=match.group('hostmask'))

                except Exception as e:
                    print "I got an error here: %s" % e
                    traceback.print_tb(sys.exc_info()[2], limit=1, file=sys.stdout)
            else:
                print(":IRC COMMAND: %s" % (match.groups()))
        except:
            if not match:
                print("******************** WARNING :::: LINE DISCARDED IN _PARSE_RAW_INPUT")
            
    def start(self):
        while 1: # Main Loop
            line = self.s.recv(1024) #recieve server messages

            if VERBOSE: print line #server message is output
            line = self._parse_raw_input(line)

    def _server_command(self, command, server):
        """
        This command is for the network layer to respond to diffrent server
        requests, like ping.
        """
        
        if command == 'PING': #If server pings then pong 
            if VERBOSE: print "replying to pong \'%s\'" % ('PONG ' + server)
            self.s.send('PONG ' + ":" + server + '\n')

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

    def management_cmd(self, command, nick, channel, **kwargs):
        """
        This Function should be extended when you want to listen too command args 
        like KICK, JOIN, PING etc.
        """
        if VERBOSE:
            print(":MANAGEMENT: Command: %s, Nick: %s, Channel: %s, Message: %s, From: %s!%s@%s" % (command, nick,
                                                                                                    channel,
                                                                                                    kwargs["msg"],
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
