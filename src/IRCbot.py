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

"""
IRC SPESIFICATION
<message> ::=
    [':' <prefix> <SPACE> ] <command> <params> <crlf>
<prefix> ::=
    <servername> | <nick> [ '!' <user> ] [ '@' <host> ]
<command> ::=
    <letter> { <letter> } | <number> <number> <number>
<SPACE> ::=
    ' ' { ' ' }
<params> ::=
    <SPACE> [ ':' <trailing> | <middle> <params> ]
<middle> ::=
    <Any *non-empty* sequence of octets not including SPACE or NUL or CR or LF, the first of which may not be ':'>
<trailing> ::=
    <Any, possibly *empty*, sequence of octets not including NUL or CR or LF>
<crlf> ::=
    CR LF 
"""

CRLF_RE = r'$' # This is not CRLF but its stripped before the RE is used, so it will be correct in our case
PARAMS_RE = r'((\s+(?P<middle>[^:](\S|(\s(?!:)))+))?(\s+:(?P<params>[^\r\n]*))?)'
COMMAND_RE = r'(?P<command>\S+)'
PREFIX_RE = r'((?P<servername>[^.!@\s]+(\.[^.!@\s]+)+)|(?P<nick>[^.\s!]+)(!(?P<ident>[^@\s]+))?(@(?P<host>[^:\s]+))?)'
MESSAGE_RE = r'^(:(?P<prefix>' + PREFIX_RE + r')\s+)?' + COMMAND_RE + PARAMS_RE + CRLF_RE

class BadIRCCommandException(Exception): pass

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
        self.message_re = re.compile(MESSAGE_RE)
        self.send_lock = Lock()
        self.exit = False
        self.rest_line = ""
        
    def __del__(self):
        self.s.close()

    def _parse_command(self, cmd):
        first_space = cmd.find(" ")
        if first_space == -1:
            return (cmd[1:], None)
        else:
            return (cmd[1:first_space], cmd[first_space + 1:])
        
    def __lineParser(self, raw):
        lines = raw.split('\r\n')
        if self.rest_line != "":
            lines[0] = self.rest_line + lines[0]
        self.rest_line = lines.pop()

        for line in lines:
            try:
                match = self.message_re.match(line)
                if IRC_DEBUG: 
                    sys.stderr.write(":BEFORE HANDLING: " + line + "\n")
                    sys.stderr.write(str(match.groupdict()) + "\n")
                
                if not match.group('prefix'):
                    self._server_command(match.group('command'), 
                                        (match.group('middle'), match.group('params')))
                else:
                    if match.group('command') == 'PRIVMSG':
                        if not match.group('middle'): 
                            raise BadIRCCommandException('A badly formated PRIVMSG appeared.')
                        msg = match.group('params')
                        channel = match.group('middle').strip()
                        arg_dict = {"from_nick":match.group('nick'),
                                    "from_ident":match.group('ident'),
                                    "from_host_mask":match.group('host')}

                        if msg[0] == COMMAND_CHAR:
                            full_cmd = self._parse_command(msg)
                            self.cmd(full_cmd[0], full_cmd[1], channel, **arg_dict)
                        elif msg[0] == HELP_CHAR:
                            full_cmd = self._parse_command(msg)
                            self.help(full_cmd[0], full_cmd[1], channel, **arg_dict)
                        else:
                            self.listen(match.group('command'), msg, channel, **arg_dict)
                    else:
                        if match.group('nick'):
                            self.management_cmd(match.group('command'), 
                                                match.group('middle').strip() if match.group('middle') else None,
                                                msg=match.group('params'),
                                                from_nick=match.group('nick'),
                                                from_ident=match.group('ident'),
                                                from_host_mask=match.group('host'))
                        else:
                            self.management_cmd(match.group('command'),
                                                match.group('middle').strip() if match.group('middle') else None,
                                                msg=match.group('params'),
                                                server_adr=match.group('servername'))
            except KeyboardInterrupt:
                raise
            except Exception as e:
                sys.stderr.write(":ERROR: " + repr(e) + "\n")
                sys.stderr.write(":LINE : \"" + line + "\"\n")
        
    def connect(self):
        self.s.connect((self.host, self.port)) #Connect to server 
        self.send_sync('NICK ' + self._nick + '\n') #Send the nick to server 
        self.send_sync('USER ' + self.ident + ' ' + self.host + ' SB: ' + self.realname + '\n') #Identify to server

        exit = False
        while not exit: # Join loop 
            raw = self.s.recv(1024) #recieve server messages 
            if not raw: break
            
            lines = raw.split('\r\n')
            if self.rest_line != "":
                lines[0] = self.rest_line + lines[0]
            self.rest_line = lines.pop()
                
            for line in lines:
                if DEBUG: 
                    sys.stderr.write(":LINE (connect): " + line + "\n") #server message is output.
                match = self.message_re.match(line)
                if not match: sys.exit(1)
                if match.group('command') == '376':
                    if VERBOSE: print(":CONNECT: MOTD FOUND!, CONNECTED")
                    exit = True
                    break

                if match.group('command') == 'PING': #If server pings then pong 
                    self.send_sync('PONG ' + match.group('params') + '\n')  

        return True

    def join(self, name):
        if not name in self.channel:
            self.send_sync('JOIN ' + name + '\n');
            exit = False
            
            while not exit:
                raw = self.s.recv(1048)
                if not raw: break
                
                lines = raw.split('\r\n')
                if self.rest_line != "":
                    lines[0] = self.rest_line + lines[0]
                self.rest_line = lines.pop()
                
                for l in lines:
                    if DEBUG: sys.stderr.write(":LINE (join): " + l + "\n")
                    match = self.message_re.match(l)
                    if match.group('command') == '353':
                        if DEBUG: sys.stderr.write(str(match.groups()) + "\n")
                        self.manage_users_during_join(name, match.group('params'))

                    elif match.group('command') == '366': 
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
        elif to != None and name == to:
            self.send_sync("PRIVMSG " + to + " :" + message + "\n")
        else:
            self.send_sync("PRIVMSG " + name + " :" + message + "\n")
            
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

    def start(self):
        try:
            while not self.exit: # Main Loop
                line = self.s.recv(1024) #recieve server messages
                if not line: break
                line = self.__lineParser(line)
        except KeyboardInterrupt:
            return

    def stop(self):
        self.s.close()
        
    def _server_command(self, command, server):
        """
        This command is for the network layer to respond to diffrent server
        requests, like ping.
        """
        if DEBUG:
            print(":SERVER: Command: %s, Server: %s" % (command, server))

        if IRC_DEBUG:
            sys.stderr.write('PONG ' + ":" + server[1] + '\n')
            
        if command == 'PING':
            self.send_sync('PONG ' + ":" + server[1] + '\n')

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
