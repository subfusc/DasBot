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
from threading import Lock
from GlobalConfig import *

IDENT_RE = r'(?P<nick>[^!]+)![~^](?P<ident>[^@]+)@(?P<hostmask>\S+)'
ADRESS_RE = r'[^!@]+(\.[^!@.\s]+)+'
CHANNEL_JOIN_RE = r'\s*:[^3]+353[^:]+:(?P<nicks>[^\r\n]+)\s*'
MESSAGE_RE = r'^(?P<svcmd>[^!@\s]+)\s+:(?P<adress>[^!@]+(.[^!@\r\n])+)\s*$|^:(' + \
    IDENT_RE + r'|(?P<adr>' + ADRESS_RE + \
    r'))\s+(?P<uscmd>\S+)\s+(?P<args>[^:\r\n]*)\s*(:(?P<msg>[^\r\n]+))?\s*$'

class IRCbot(object):

    def __init__(self):
        """ 
        Make an instance of the IRCbot class and prepare it for a Connection 
        """
        self.host = HOST #: The IP/URL for the server
        self.port = PORT #: The port number for the server 
        self._nick = NICK #: The nick the bot is going to use
        self.ident = IDENT #: Identity of the bot
        self.realname = REAL_NAME #: The "realname" of the bot
        self.s = socket.socket() #: Create a socket for the I/O to the server
        self.s.settimeout(600)
        self.ident_re = re.compile(IDENT_RE) 
        self.channel_join_re = re.compile(CHANNEL_JOIN_RE) 
        self.message_re = re.compile(MESSAGE_RE)
        self.send_lock = Lock()
        self.exit = False
        
    def __del__(self):
        self.s.close()

    def connect(self):
        self.s.connect((self.host, self.port)) #Connect to server 
        self.send_sync('NICK ' + self._nick + '\n') #Send the nick to server 
        self.send_sync('USER ' + self.ident + ' ' + self.host + ' SB: ' + self.realname + '\n') #Identify to server

        while 1: # Join loop 
            line = self.s.recv(1024) #recieve server messages 
            if not line: break
            if DEBUG: print line #server message is output 
            line = line.rstrip() #remove trailing 'rn' 
            line = line.split()

            if '376' in line:
                if VERBOSE: print(":CONNECT: MOTD FOUND!, CONNECTED")
                break

            if len(line) > 1 and line[0] == 'PING': #If server pings then pong 
                self.send_sync('PONG ' + line[1] + '\n')  

        return True

    def join(self, name):
        if not name in self.channel:
            self.send_sync('JOIN ' + name + '\n');

            exit = False
            while not exit:
                line = self.s.recv(2048)
                if not line: break
                for l in line.split('\n'):
                    if DEBUG: print "IN FOR: ", l
                        
                    match = self.channel_join_re.match(l)
                    if match:
                        if DEBUG: print match.groups()
                        self.manage_users_during_join(name, match.group('nicks'))

                    if l.find(' 366 ') != -1: 
                        exit = True
                        break
            return True
        else:
            return True

    def manage_users_during_join(self, name, args): pass
        
    def part(self, name):
        if name in self.channel:
            self.send_sync('PART ' + name + '\n')
            del self.channel[name]
        return True

    def msg(self, name, message, to = None):
        if name[0] == '#':
            if to: self.send_sync("PRIVMSG " + name + " :" + to + ": " + message + "\n")
            else: self.send_sync("PRIVMSG " + name + " :" + message + "\n")
        elif to != None:
            self.send_sync("PRIVMSG " + to + " :" + message + "\n")

    def private_msg(self, to, message):
        self.send_sync("PRIVMSG %s :%s\n" % (to, message))

    def notify(self, name, message):
        self.send_sync("NOTICE " + name + " :" + message + "\n")

    def topic(self, channel, topic):
        self.send_sync("TOPIC " + channel + " :" + topic + "\n")

    def nick(self, _nick):
        self.send_sync("NICK " + _nick + "\n")
        self._nick = _nick

    def kick(self, channel, nick, message="I don't like you!"):
        print "KICK " + channel + " " + nick + " :" + message
        self.send_sync("KICK " + channel + " " + nick + " :" + message + "\n")

    def ban(self, channel, nick="*", ident="*", hostmask="*"):
        if not (nick == "*" and ident == "*" and hostmask == "*"):
            self.send_sync("MODE " + channel + " +b %s!%s@%s\n" % (nick, ident, hostmask))

    def unban(self, channel, nick="*", ident="*", hostmask="*"):
        self.send_sync("MODE " + channel + " -b %s!%s@%s\n" % (nick, ident, hostmask))

    def op(self, channel, nick): 
        self.send_sync("MODE " + channel + " +o " + nick + "\n")

    def deop(self, channel, nick): 
        self.send_sync("MODE " + channel + " -o " + nick + "\n")

    def voice(self, channel, nick): 
        self.send_sync("MODE " + channel + " +v " + nick + "\n")

    def devoice(self, channel, nick): 
        self.send_sync("MODE " + channel + " -v " + nick + "\n")
        
    def send_sync(self, msg):
        self.send_lock.acquire()
        self.s.send(msg)
        self.send_lock.release()
        
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
            line = line.split('\n')
            if IRC_DEBUG: print line
            for l in line[:-1]:
                match = self.message_re.match(l)

                if not match:
                    print(":ERROR: '" + str(l) + "' doesn't match the regex.")
                    continue

                if IRC_DEBUG:
                    print(match.groups())

                if match.group('svcmd'):
                    self._server_command(match.group('svcmd'), match.group('adress'))
                    continue

                if match.group('uscmd') == 'PRIVMSG':
                    try:
                        channel = match.group('args').strip()
                        channel = match.group('nick') if channel == NICK else channel
                        if match.group('msg')[0] == COMMAND_CHAR:
                            first_space = match.group('msg').find(" ")
                            self.cmd(match.group('msg')[1:first_space] if first_space != -1 else match.group('msg')[1:],
								match.group('msg')[first_space + 1:].strip() if first_space != -1 else None,
								channel,
								from_nick=match.group('nick'),
								from_ident=match.group('ident'),
								from_host_mask=match.group('hostmask'))
                        elif match.group('msg')[0] == HELP_CHAR:
                            first_space = match.group('msg').find(" ", 2)
                            self.help(match.group('msg')[1:first_space].strip() if first_space != -1 else match.group('msg')[1:].strip(),
								match.group('msg')[first_space + 1:].strip() if first_space != -1 else None,
                                channel,
								from_nick=match.group('nick'),
								from_ident=match.group('ident'),
								from_host_mask=match.group('hostmask'))
                        else:
                            self.listen(match.group('uscmd'), match.group('msg'), channel,
								from_nick=match.group('nick'),
								from_ident=match.group('ident'),
								from_host_mask=match.group('hostmask'))
                    except KeyboardInterrupt:
                        self.exit = True
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
        except KeyboardInterrupt:
            self.exit = True
        except Exception as e:
            if IRC_DEBUG:
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
        try:
            while not self.exit: # Main Loop
                line = self.s.recv(1024) #recieve server messages
                if not line: break
                if IRC_DEBUG: print line #server message is output
                line = self._parse_raw_input(line)
        except KeyboardInterrupt:
            return

    def stop(self):
        self.s.close()
        
    def _server_command(self, command, server):
        """
        This command is for the network layer to respond to diffrent server
        requests, like ping.
        """
        if VERBOSE:
            print(":SERVER: Command: %s, Server: %s" % (command, server))

        if command == 'PING':
            self.send_sync('PONG ' + ":" + server + '\n')

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

    def management_cmd(self, command, args, **kwargs):
        """
        This Function should be extended when you want to listen too command args 
        like KICK, JOIN, PART etc.
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
            self.notify(kwargs["from_nick"], "?cmd - Will give you help on command cmd.")
            self.notify(kwargs["from_nick"], "?all - Will give you a list of available commands.")
        if VERBOSE:
            print(":HELP: Command: %s, Message: %s, Channel: %s, From: %s!%s@%s" % (command, args, channel,
				kwargs["from_nick"], 
				kwargs["from_ident"],
				kwargs["from_host_mask"]))
