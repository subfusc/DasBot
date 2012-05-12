# -*- coding: utf-8 -*-
# Basic interface class for communicating with an IRC server.
# Copyright (C) 2012  Sindre Wetjen

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys 
import socket 
import string 
import re
import traceback
import time
from GlobalConfig import *

IDENT_RE = r'(?P<nick>[^!]+)![~^](?P<ident>[^@]+)@(?P<hostmask>\S+)'
ADRESS_RE = r'[^!@]+(\.[^!@.\s]+)+'
CHANNEL_JOIN_RE = r'\s*:[^3]+353[^:]+:(?P<nicks>[^\r\n]+)\s*'
MESSAGE_RE = r'^(?P<svcmd>[^!@\s]+)\s+:(?P<adress>[^!@]+(.[^!@\r\n])+)\s*$|^:(' + \
    IDENT_RE + r'|(?P<adr>' + ADRESS_RE + \
    r'))\s+(?P<uscmd>\S+)\s+(?P<args>[^:\r\n]*)\s*(:(?P<msg>[^\r\n]+))?\s*$'

class IRCbot(object):

    def __init__(self, host, port, nick, ident, realname):
        """ 
        Make an instance of the IRCbot class and prepare it for a Connection 
        """
        self.host = host #: The IP/URL for the server
        self.port = port #: The port number for the server 
        self._nick = nick #: The nick the bot is going to use
        self.ident = ident #: Identity of the bot
        self.realname = realname #: The "realname" of the bot
        self.s = socket.socket() #: Create a socket for the I/O to the server
        self.channel = {} #: Channels we are in
        self.ident_re = re.compile(IDENT_RE) 
        self.channel_join_re = re.compile(CHANNEL_JOIN_RE) 
        self.message_re = re.compile(MESSAGE_RE)
        if RAWLOG: self.log = open(RAWLOG_FILE, 'a')

    def connect(self):
        self.s.connect((self.host, self.port)) #Connect to server 
        self.s.send('NICK ' + self._nick + '\n') #Send the nick to server 
        self.s.send('USER ' + self.ident + ' ' + self.host + ' SB: ' + self.realname + '\n') #Identify to server

        while 1: # Join loop 
            line = self.s.recv(1024) #recieve server messages 
            if DEBUG: print line #server message is output 
            line = line.rstrip() #remove trailing 'rn' 
            line = line.split()

            if '376' in line:
                if VERBOSE: print(":CONNECT: MOTD FOUND!, CONNECTED")
                break

            if len(line) > 1 and line[0] == 'PING': #If server pings then pong 
                self.s.send('PONG ' + line[1] + '\n')  

        return True

    def join(self, name):
        if not name in self.channel:
            self.channel[name] = {'op':[], 'voice':[], 'user':[]}
            self.s.send('JOIN ' + name + '\n');

            exit = False
            while not exit:
                line = self.s.recv(2048)
                if RAWLOG: self.log.write(line)
                for l in line.split('\n'):
                    if DEBUG: print "IN FOR: ", l
                        
                    match = self.channel_join_re.match(l)
                    if match:
                        if DEBUG: print match.groups()
                        nicks = match.group('nicks')
                        nicks = nicks.split()
                        for nick in nicks:
                            if nick[0] == "+":
                                self.channel[name]['voice'].append(nick[1:])
                            elif nick[0] == "@":
                                self.channel[name]['op'].append(nick[1:])
                            else:
                                self.channel[name]['user'].append(nick)

                    if DEBUG: print(self.channel[name])

                    if l.find(' 366 ') != -1: 
                        exit = True
                        break
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

    def kick(self, channel, nick, message="I don't like you!"):
        print "KICK " + channel + " " + nick + " :" + message
        self.s.send("KICK " + channel + " " + nick + " :" + message + "\n")

    def ban(self, channel, nick="*", ident="*", hostmask="*"):
        if not (nick == "*" and ident == "*" and hostmask == "*"):
            self.s.send("MODE " + channel + " +b %s!%s@%s\n" % (nick, ident, hostmask))

    def unban(self, channel, nick="*", ident="*", hostmask="*"):
        self.s.send("MODE " + channel + " -b %s!%s@%s\n" % (nick, ident, hostmask))

    def user_in_channel(self, channel, nick):
        channel = self.channel[channel]
        return nick in channel["user"] or nick in channel["voice"] or nick in channel["op"] 

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
	    if RAWLOG: 
			self.log.write(time.strftime("%D %H:%M"))
			self.log.write(line)
			line = line.split('\n')
            if DEBUG: print line
            for l in line[:-1]:
                match = self.message_re.match(l)

                if DEBUG:
                    print(match.groups())

                if match.group('svcmd'):
                    self._server_command(match.group('svcmd'), match.group('adress'))
                    return

                if match.group('uscmd') == 'PRIVMSG':
                    try:
                        if match.group('msg')[0] == COMMAND_CHAR:
                            first_space = match.group('msg').find(" ")
                            self.cmd(match.group('msg')[1:first_space] if first_space != -1 else match.group('msg')[1:],
								match.group('msg')[first_space + 1:].strip() if first_space != -1 else None,
								match.group('args').strip(),
								from_nick=match.group('nick'),
								from_ident=match.group('ident'),
								from_host_mask=match.group('hostmask'))
                        elif match.group('msg')[0] == HELP_CHAR:
                            first_space = match.group('msg').find(" ", 2)
                            self.help(match.group('msg')[1:first_space].strip() if first_space != -1 else match.group('msg')[1:].strip(),
								match.group('msg')[first_space + 1:].strip() if first_space != -1 else None,
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
                    #TODO parse for management
                    if DEBUG: print(":IRC COMMAND: %s" % str(match.groups()))
                    if match.group('nick'):
                        self.management_cmd(match.group('uscmd'), 
							match.group('args').strip(),
							msg=match.group('msg'), 
							from_nick=match.group('nick'),
							from_ident=match.group('ident'),
							from_host_mask=match.group('hostmask'))
                    else:
                        self.management_cmd(match.group('uscmd'), 
							match.group('args').strip(),
							msg=match.group('msg'), 
							server_adr=match.group('adr'))
        except Exception as e:
            print("ERROR: %s" % e)
            if not match:
                print("******************** WARNING :::: LINE DISCARDED IN _PARSE_RAW_INPUT")
                print(line)
                newline = False
                for char in line: 
                    if re.match('\\s', char): 
                        print(ord(char)),
                        newline = True
                    else:
                        if newline:
                            print("")
                            newline = False 
                print("")
                print("******************** END WARNING ::::")

    def start(self):
        while 1: # Main Loop
            line = self.s.recv(1024) #recieve server messages

            if DEBUG: print line #server message is output
            line = self._parse_raw_input(line)

    def _server_command(self, command, server):
        """
        This command is for the network layer to respond to diffrent server
        requests, like ping.
        """
        if VERBOSE:
            print(":SERVER: Command: %s, Server: %s" % (command, server))

        if command == 'PING':
            self.s.send('PONG ' + ":" + server + '\n')

    def cmd(self, command, args, channel, **kwargs):
        """
        This function, when extended in your class, will give you all commands (as determined by
        the globalconf COMMAND_CHAR) written in a channel.
        If you are only going to run commands and not doing anything with NLP, please extend this
        to avoid unecessary overhead.
        """
        if VERBOSE:
            print(":COMMAND: Command: %s, Args: %s, Channel: %s, From: %s!%s@%s" % (command, args, 
				channel,
				kwargs["from_nick"], 
				kwargs["from_ident"],
				kwargs["from_host_mask"]))   

    def __rm_user(self, channel, nick):
        channel = self.channel[channel]
        if nick in channel["user"]: 
            x = channel["user"].index(nick)
            del(channel["user"][x])
        elif nick in channel["voice"]: del(channel["voice"][channel["voice"].index(nick)])
        elif nick in channel["op"]: del(channel["op"][channel["op"].index(nick)])

    def management_cmd(self, command, args, **kwargs):
        """
        This Function should be extended when you want to listen too command args 
        like KICK, JOIN, PING etc.
        """
        if VERBOSE:
            if "from_nick" in kwargs:
                print(":MANAGEMENT: Command: %s, Args: %s, Message: %s, From: %s!%s@%s" % (command,
					args,
					kwargs["msg"],
					kwargs["from_nick"], 
					kwargs["from_ident"],
					kwargs["from_host_mask"]))
            else:
                print(":MANAGEMENT: Command: %s, Args: %s, Message: %s, From: %s" % (command,
					args,
					kwargs["msg"],
					kwargs["server_adr"]))
        if command == "JOIN":
            self.channel[kwargs["msg"]]["user"].append(kwargs["from_nick"])
        elif command == "QUIT":
            for c in self.channel:
                self.__rm_user(c, kwargs["from_nick"])
        elif command == "PART":
            self.__rm_user(args, kwargs["msg"])
        elif command == "KICK":
            args = args.split()
            self.__rm_user(args[0], args[1])
        elif command == "MODE":
            args = args.split()
            if len(args) == 3:
                if args[1] == "+o":
                    self.__rm_user(args[0], args[2])
                    self.channel[args[0]]["op"].append(args[2])
                elif args[1] == "-o":
                    self.__rm_user(args[0], args[2])
                    self.channel[args[0]]["user"].append(args[2])
                elif args[1] == "+v":
                    self.__rm_user(args[0], args[2])
                    self.channel[args[0]]["voice"].append(args[2])
                elif args[1] == "-v":
                    self.__rm_user(args[0], args[2])
                    self.channel[args[0]]["user"].append(args[2])

    def listen(self, command, msg, channel, **kwargs):
        """
        This Function is supposed to be extended in subclasses to provide functionality when you
        want all sentences, and not just commands. If you want only commands, please extend
        cmd.
        """
        if VERBOSE:
            print(":LISTEN: Command: %s, Message (%d): %s, Channel: %s, From: %s!%s@%s" % (command, len(msg), msg, 
				channel,
				kwargs["from_nick"], 
				kwargs["from_ident"],
				kwargs["from_host_mask"]))

    def help(self, command, args, channel, **kwargs):
        """
        The function that should be extended in order to provide help to user for your command.
        Command is the command the user is asking help for.
        Args are ... well args...
        channel is the channel the help request came from.
        """
        if command == "":
            self.notify(kwargs["from_nick"], "? CMD - Will give you help on a given command.")
            self.notify(kwargs["from_nick"], "? all - Will give you a list of available commands.")
        if VERBOSE:
            print(":HELP: Command: %s, Message: %s, Channel: %s, From: %s!%s@%s" % (command, args, channel,
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
