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

import threading
import sys 
import socket 
import string 
import re
import traceback
import time
import GlobalConfig as conf
from threading import Lock
VERSION = "0.24a"

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

class SynchronizedQueue(object):

    def __init__(self):
        self.lock = Lock()
        self.queue = []

    def add(self, obj):
        self.lock.acquire()
        self.queue.append(obj)
        self.lock.release()

    def sneak(self, obj):
        self.lock.acquire()
        self.queue.insert(0, obj)
        self.lock.release()

    def pop(self):
        self.lock.acquire()
        rval = self.queue.pop()
        self.lock.release()
        return rval

    def clear(self):
        self.lock.acquire()
        self.queue = []
        self.lock.release()
    
    def empty(self):
        return len(self.queue) == 0
        
class SocketKeeper(threading.Thread):

    def __init__(self, host, port, timeout=600, wait_delay=10, max_lines=2):
        super(SocketKeeper, self).__init__()
        self.host = host 
        self.port = port
        self.timeout = timeout
        self.wait_delay = wait_delay
        self.max_lines = max_lines
        
        self.exit = False
        self.connect_mode = True
        self.queue_event = threading.Event()
        
        self.s = None
        self.plugin_queue = SynchronizedQueue()
        self.core_queue = SynchronizedQueue()
        
        self.timestamps = []

    def copy_constructor(self):
        rval = SocketKeeper(self.host, self.port, timeout=self.timeout, wait_delay=self.wait_delay, max_lines=self.max_lines)
        rval.plugin_queue = self.plugin_queue
        if self.s: self.s.close()
        return rval
        
    def __connect(self):
        if self.s: 
            self.s.close()
        self.s = socket.socket()
        self.s.settimeout(self.timeout)
        self.s.connect((self.host, self.port))

    def __disconnect(self):
        if self.s: self.s.close()


    def __clean_timestamps(self, ctime):
        for i, d in enumerate(self.timestamps):
            if (ctime - d) > self.wait_delay:
                del(self.timestamps[i]) 
            
    def __delay_send(self, string):
        print "Delay send"
        ctime = time.time()
        self.__clean_timestamps(ctime)

        print self.timestamps
        print ctime
        
        if len(self.timestamps) > self.max_lines:
            wait_time = self.wait_delay - (ctime - self.timestamps[0])
            print "waiting: ", wait_time
            if wait_time > 0:
                time.sleep(wait_time)
            del(self.timestamps[0])

        self.timestamps.append(ctime)
        self.s.send(string)
        
    def __non_delay_send(self, string):
        print "non delay send"
        self.timestamps.append(time.time())
        if len(self.timestamps) > 1000:
            self.__clean_timestamps(time.time())
            
        self.s.send(string)
        
    def connecting(self):
        print "Trying to connect"
        self.connect_mode = True
        self.__connect()
        self.core_queue.clear()

    def connected(self):
        self.connect_mode = False
        self.queue_event.set()
        
    def stop(self):
        print "STOOOP"
        self.exit = True
        self.queue_event.set()
            
    def send(self, string):
        print "send", string
        self.plugin_queue.add(string)
        self.queue_event.set()

    def core_send(self, string):
        self.core_queue.add(string)
        self.queue_event.set()
        
    def ping(self, string):
        self.core_queue.sneak(string)
        self.queue_event.set()

    def recv(self, length):
        return self.s.recv(length)
        
    def run(self):
        print "STAAART"
        self.exit = False
        
        try:
            while not self.exit:
                print "LOOOOOP"
                cobj = None
                self.queue_event.clear()

                print "CUE: ", self.core_queue.empty(), self.plugin_queue.empty(), self.plugin_queue.queue
                while not self.core_queue.empty():
                    print "poping core cue"
                    self.__non_delay_send(self.core_queue.pop())
                    self.queue_event.clear()
                
                if not self.connect_mode:
                    while self.core_queue.empty() and not self.plugin_queue.empty():
                        print "poping plugin cue"
                        cobj = self.plugin_queue.pop()
                        self.__delay_send(cobj)
                        cobj
                        self.queue_event.clear()
                        
                if self.core_queue.empty() and self.plugin_queue.empty():
                    print "wait for event"
                    self.queue_event.wait()
                    
        except socket.error:
            sys.stderr.write("Inside Socket Error: {0}".format(socket.error))
            if cobj: self.queue.sneak(cobj)

        self.__disconnect()
        
    
class IRCbot(object):

    def __init__(self, **kwargs):
        """ 
        Make an instance of the IRCbot class and prepare it for a Connection 
        """
        self.host = conf.HOST
        self.port = conf.PORT
        self._nick = conf.NICK #: The nick the bot is going to use
        self.ident = conf.IDENT #: Identity of the bot
        self.realname = conf.REAL_NAME #: The "realname" of the bot
        self.s = None  #: Create a socket for the I/O to the server
        self.message_re = re.compile(MESSAGE_RE)
        self.exit = False
        self.rest_line = ""
        
    def __del__(self):
        if self.s: self.s.stop()

    def _parse_command(self, cmd):
        first_space = cmd.find(" ")
        if first_space == -1:
            return (cmd[1:], None)
        else:
            return (cmd[1:first_space], cmd[first_space + 1:])

    def reset(self):
        "Reset variables that are needed in order to reconnect on pingout."
        if self.s: 
            self.s.stop()
            self.s = self.s.copy_constructor()
        else:
            self.s = SocketKeeper(conf.HOST, conf.PORT)
            
    def __lineParser(self, raw):
        lines = raw.split('\r\n')
        if self.rest_line != "":
            lines[0] = self.rest_line + lines[0]
        self.rest_line = lines.pop()

        for line in lines:
            try:
                match = self.message_re.match(line)
                if conf.IRC_DEBUG: 
                    sys.stderr.write(":BEFORE HANDLING: " + line + "\r\n")
                    sys.stderr.write(str(match.groupdict()) + "\r\n")
                
                if not match.group('prefix'):
                    self._server_command(match.group('command'), 
                                        (match.group('middle'), match.group('params')))
                else:
                    if match.group('command') == 'PRIVMSG':
                        if not match.group('middle'): 
                            raise BadIRCCommandException('A badly formated PRIVMSG appeared.')
                        msg = match.group('params')
                        channel = match.group('middle').strip() if match.group('middle').strip() != conf.NICK else match.group('nick')
                        arg_dict = {"from_nick":match.group('nick'),
                                    "from_ident":match.group('ident'),
                                    "from_host_mask":match.group('host'),
                                    "version":VERSION}

                        if msg[0] == conf.COMMAND_CHAR:
                            full_cmd = self._parse_command(msg)
                            self.cmd(full_cmd[0], full_cmd[1], channel, **arg_dict)
                        elif msg[0] == conf.HELP_CHAR:
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
                                                from_host_mask=match.group('host'),
                                                version=VERSION)
                        else:
                            self.management_cmd(match.group('command'),
                                                match.group('middle').strip() if match.group('middle') else None,
                                                msg=match.group('params'),
                                                server_adr=match.group('servername'))
            except KeyboardInterrupt:
                raise
            except Exception as e:
                sys.stderr.write(":ERROR: " + repr(e) + "\r\n")
                sys.stderr.write(":LINE : \"" + line + "\"\n")
        
    def connect(self):
        self.reset()
        self.s.connecting() #Connect to server
        self.s.start()
        self.send_sync('NICK ' + self._nick + '\r\n') #Send the nick to server 
        self.send_sync('USER ' + self.ident + ' ' + self.host + ' SB: ' + self.realname + '\r\n') #Identify to server

        exit = False
        while not exit: # Join loop 
            raw = self.s.recv(1024) #recieve server messages 
            if not raw: return False
            
            lines = raw.split('\r\n')
            if self.rest_line != "":
                lines[0] = self.rest_line + lines[0]
            self.rest_line = lines.pop()
                
            for line in lines:
                if conf.DEBUG: 
                    sys.stderr.write(":LINE (connect): " + line + "\n") #server message is output.
                match = self.message_re.match(line)
                if not match: sys.exit(1)
                if match.group('command') == '376':
                    if conf.VERBOSE: print(":CONNECT: MOTD FOUND!, CONNECTED")
                    exit = True
                    break

                if match.group('command') == 'PING': #If server pings then pong 
                    self.send_sync('PONG ' + match.group('params') + '\r\n')

        for channel in conf.STARTUP_CHANNELS:
            self.join(channel)
        self.s.connected()
            
        return True

    def manage_users_during_join(self, name, args): pass
    def manage_topic_during_join(self, channel, topic): pass
        
    def join(self, name):
        if not name in self.channel:
            self.send_sync('JOIN ' + name + '\r\n');
            exit = False
            
            while not exit:
                raw = self.s.recv(1048)
                if not raw: break
                
                lines = raw.split('\r\n')
                if self.rest_line != "":
                    lines[0] = self.rest_line + lines[0]
                self.rest_line = lines.pop()
                
                for l in lines:
                    if conf.DEBUG: sys.stderr.write(":LINE (join): " + l + "\r\n")
                    match = self.message_re.match(l)
                    if match.group('command') == '353':
                        self.manage_users_during_join(match.group('middle').split("=")[1].strip(),
                                                      match.group('params'))
                        # if DEBUG: sys.stderr.write(str(match.groups()) + "\n")
                    elif match.group('command') == '366': 
                        exit = True
                        break
                    elif match.group('command') == '332':
                        self.manage_topic_during_join(match.group('middle').split()[1].strip(),
                                                      match.group('params'))
                    elif match.group('command') == "PING":
                        self.send_sync('PONG ' + match.group('params') + '\r\n')
            return True
        else:
            return True
        
    def part(self, name):
        if name in self.channel:
            self.send_sync('PART ' + name + '\r\n')
            del self.channel[name]
        return True

    def msg(self, name, message, to = None, core=True):
        if name[0] == '#':
            if to: self.send_sync("PRIVMSG " + name + " :" + to + ": " + message + "\r\n", core=core)
            else: self.send_sync("PRIVMSG " + name + " :" + message + "\r\n", core=core)
        elif to != None and name == to:
            self.send_sync("PRIVMSG " + to + " :" + message + "\r\n", core=core)
        else:
            self.send_sync("PRIVMSG " + name + " :" + message + "\r\n", core=core)
            
    def private_msg(self, to, message, core=True):
        self.send_sync("PRIVMSG %s :%s\n" % (to, message), core=core)

    def notify(self, name, message, core=True):
        self.send_sync("NOTICE " + name + " :" + message + "\r\n", core=core)

    def topic(self, channel, topic, core=True):
        self.send_sync("TOPIC " + channel + " :" + topic + "\r\n", core=core)

    def nick(self, _nick):
        self.send_sync("NICK " + _nick + "\r\n")
        self._nick = _nick

    def kick(self, channel, nick, message="I don't like you!"):
        print "KICK " + channel + " " + nick + " :" + message
        self.send_sync("KICK " + channel + " " + nick + " :" + message + "\r\n")

    def ban(self, channel, nick="*", ident="*", hostmask="*"):
        if not (nick == "*" and ident == "*" and hostmask == "*"):
            self.send_sync("MODE " + channel + " +b %s!%s@%s\n" % (nick, ident, hostmask))

    def unban(self, channel, nick="*", ident="*", hostmask="*"):
        self.send_sync("MODE " + channel + " -b %s!%s@%s\n" % (nick, ident, hostmask))

    def op(self, channel, nick):
        self.send_sync("MODE " + channel + " +o " + nick + "\r\n")

    def deop(self, channel, nick): 
        self.send_sync("MODE " + channel + " -o " + nick + "\r\n")

    def voice(self, channel, nick): 
        self.send_sync("MODE " + channel + " +v " + nick + "\r\n")

    def devoice(self, channel, nick): 
        self.send_sync("MODE " + channel + " -v " + nick + "\r\n")

    def send_sync(self, msg, core=True):
        if core:
            self.s.core_send(msg)
        else:
            self.s.send(msg)

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

    def start(self, reconnect=True, reconnect_timeout=5, tries=10):
        original_tries = tries
        self.connect()
        rec = False

        try:
            while not self.exit: # Main Loop
                try:
                    if rec == True:
                        if reconnect and tries > 0:
                            sys.stderr.write("Waiting: {0}".format(reconnect_timeout))
                            time.sleep(reconnect_timeout)
                            if self.connect():
                                tries = original_tries
                                rec = False
                            else: tries -= 1
                        else: break
                        
                    line = self.s.recv(1024) #recieve server messages
                    if not line: continue
                    
                    line = self.__lineParser(line)
                except socket.error:
                    sys.stderr.write("We got a Socket error: {0}.".format(socket.error))
                    rec = True

        except KeyboardInterrupt:
            self.stop()
            print "Stopping"
            return
        except Exception:
            self.stop()
            print sys.stderr >> "Got an unexpected error!!!!!!!!!!!!!!!!"
            print sys.stderr >> Exception
            
        print "stopping main"

    def stop(self):
        self.s.stop()
        
    def _server_command(self, command, server):
        """
        This command is for the network layer to respond to diffrent server
        requests, like ping.
        """
        if conf.DEBUG:
            print(":SERVER: Command: %s, Server: %s" % (command, server))

        if conf.IRC_DEBUG:
            sys.stderr.write('PONG ' + ":" + server[1] + '\r\n')
            
        if command == 'PING':
            self.send_sync('PONG ' + ":" + server[1] + '\r\n')

    def cmd(self, command, args, channel, **kwargs):
        """
        This function, when extended in your class, will give you all commands (as determined by
         the globalconf COMMAND_CHAR) written in a channel.
        If you are only going to run commands and not doing anything with NLP, please extend this
        to avoid unecessary overhead.
        """
        if conf.VERBOSE:
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
        if conf.VERBOSE:
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
        if conf.VERBOSE:
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
        if conf.VERBOSE:
            print(":HELP: Command: %s, Message: %s, Channel: %s, From: %s!%s@%s" % (command, args, channel,
				kwargs["from_nick"], 
				kwargs["from_ident"],
				kwargs["from_host_mask"]))
