# -*- coding: utf-8 -*-
# Provide plugin handing for an IRC bot
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
from IRCbot import IRCbot
import sys
import IRCFonts
from GlobalConfig import *
from os import listdir
from sys import stderr

class PluginBot(IRCbot):

    def __init__(self):
        super(PluginBot, self).__init__()
        self.__plugins = None
        self.__functions = [[], [], [], [], [], [], []]
        if 'LOAD_PLUGINS' in locals() or 'LOAD_PLUGINS' in globals() and isinstance(LOAD_PLUGINS, list):
            for plugin in LOAD_PLUGINS:
                self.__load_plugin(plugin)

    def stop(self):
        super(PluginBot, self).stop()
        for obj, attr in zip(self.__functions[1], self.__functions[5]):
            if attr:
                obj.stop()

    def _sanitize_messages(self, message_array):
        for msg in message_array:
            if type(msg) == unicode:
                return True
                
    def _send_message(self, message_array):
        if message_array == None: return

        if self._sanitize_messages(message_array): 
            self.msg("Warning, I found a undecoded unicode string", message[2])
            sys.err.write("Warning, I found a undecoded unicode string\n")
            return
        
        for message in message_array: 
            if message[0] == 0:
                if len(message) == 4:
                    self.msg(message[1], message[3], to = message[2])
                elif len(message) == 3:
                    self.msg(message[1], message[2])
            else:
                if len(message) == 3:
                    self.notify(message[1], message[2])

    def __load_plugin(self, name):
        try:
            self.__plugins = __import__('plugins.' + name, globals(), locals(), [], -1)
            plugin = eval('plugins.' + name + '.' + 'Plugin()', globals(), {"plugins":self.__plugins})
            self.__functions[0].append(name)
            self.__functions[1].append(plugin)
            self.__functions[2].append(hasattr(plugin, 'cmd'))
            self.__functions[3].append(hasattr(plugin, 'listen'))
            self.__functions[4].append(hasattr(plugin, 'help'))
            self.__functions[5].append(hasattr(plugin, 'stop'))
            self.__functions[6].append([])
            return True
        except Exception as e:
            stderr.write(repr(e) + "\n")
            return False

    def __system_unload(self, name):
        x = []
        for module in sys.modules:
            if module.startswith(('plugins.' + name)):
                x.append(module)
        for module in x:
            del(sys.modules[module])

    def __has_plugin(self, name):
        for module in self.__functions[0]:
            if name == module: return True
        return False
            
    def __unload_plugin(self, name):
        try:
            index = self.__functions[0].index(name)
            if self.__functions[5][index]:
                self.__functions[1][index].stop()
            self.__system_unload(name)
            del(self.__functions[0][index])
            del(self.__functions[1][index])
            del(self.__functions[2][index])
            del(self.__functions[3][index])
            del(self.__functions[4][index])
            del(self.__functions[5][index])
            del(self.__functions[6][index])
            return True
        except Exception as e:
            stderr.write(repr(e) + "\n")
            return False

    def __blacklist_plugin(self, plugin, channel):
        try:
            index = self.__functions[0].index(plugin)
            self.__functions[6][index].append(channel)
            return True
        except Exception as e:
            stderr.write(repr(e) + "\n")
            return False

    def __whitelist_plugin(self, plugin, channel):
        try:
            index = self.__functions[0].index(plugin)
            chan_index = self.__functions[6][index].index(channel)
            del(self.__functions[6][index][chan_index])
            return True
        except Exception as e:
            stderr.write(repr(e) + "\n")
            return False
    def __get_blacklisted(self, channel):
        rarr = []
        for plugin, blacklist in zip(self.__functions[0], self.__functions[6]):
            if channel in blacklist:
                rarr.append(plugin)
        return rarr
        
    def cmd(self, command, args, channel, **kwargs):
        if DEBUG: stderr.write("PluginBot CMD\n")
        if kwargs['auth_nick'] != None:
            if kwargs['auth_level'] >= 90:
                if command == "load" and args:
                    if self.__has_plugin(args): 
                        self.msg(channel, "Starting {p}:    [ {s} ]".format(p = args, s = IRCFonts.green(IRCFonts.bold('DONE'))))
                    elif self.__load_plugin(args):
                        self.msg(channel, "Starting {p}:    [ {s} ]".format(p = args, s = IRCFonts.green(IRCFonts.bold('DONE'))))
                    else: 
                        self.msg(channel, "Starting {p}:    [ {s} ]".format(p = args, s = IRCFonts.red(IRCFonts.bold('FAIL'))))

                elif command == "unload" and args:
                    if self.__unload_plugin(args):
                        self.msg(channel, "Stopping {p}:    [ {s} ]".format(p = args, s = IRCFonts.green(IRCFonts.bold('DONE'))))
                    else: 
                        self.msg(channel, "Stopping {p}:    [ {s} ]".format(p = args, s = IRCFonts.red(IRCFonts.bold('FAIL'))))

                elif command == "reload" and args:
                    if self.__unload_plugin(args) and self.__load_plugin(args):
                        self.msg(channel, "Reloading {p}:    [ {s} ]".format(p = args, s = IRCFonts.green(IRCFonts.bold('DONE'))))
                    else:
                        self.msg(channel, "Reloading {p}:    [ {s} ]".format(p = args, s = IRCFonts.red(IRCFonts.bold('FAIL'))))

                elif command == "blacklist":
                    if args:
                        chan = None
                        a = args.split(" ")
                        if len(a) == 1 and a[0] != '#': 
                            chan = channel
                            a = a[0]
                        elif len(a) >= 2 and a[1][0] == '#' and self.in_channel(a[1]): 
                            chan = a[1]
                            a = a[0]
                        else:
                            self.msg(channel, "You have not provided me with a correct number of arguments.", to = kwargs['from_nick'])

                        print("BLACKLIST: " + a + " " + chan)
                        if chan and self.__blacklist_plugin(a, chan):
                            self.msg(channel, "Blacklisting {p} from {c}:    [ {s} ]".format(p = a, c = chan, s = IRCFonts.green(IRCFonts.bold('DONE'))))
                        else:
                            self.msg(channel, "Blacklisting {p} from {c}:    [ {s} ]".format(p = a, c = chan, s = IRCFonts.red(IRCFonts.bold('FAIL'))))
                    else:
                        self.msg(channel, "Blacklisted in {c}: ".format(c = channel) + str(self.__get_blacklisted(channel)), to = kwargs['from_nick'])
                        
                elif command == "whitelist":
                    if args:
                        chan = None
                        a = args.split(" ")
                        if len(a) == 1 and a[0] != '#': 
                            chan = channel
                            a = a[0]
                        elif len(a) >= 2 and a[1][0] == '#' and self.in_channel(a[1]): 
                            chan = a[1]
                            a = a[0]
                        else:
                            self.msg(channel, "You have not provided me with a correct number of arguments.", to = kwargs['from_nick'])

                        print("BLACKLIST: " + a + " " + chan)
                        if chan and self.__whitelist_plugin(a, chan):
                            self.msg(channel, "Whitelisting {p} from {c}:    [ {s} ]".format(p = a, c = chan, s = IRCFonts.green(IRCFonts.bold('DONE'))))
                        else:
                            self.msg(channel, "Whitelisting {p} from {c}:    [ {s} ]".format(p = a, c = chan, s = IRCFonts.red(IRCFonts.bold('FAIL'))))
                            
            if kwargs['auth_level'] >= 98:
                if command == "forceunload":
                    self.__system_unload(args)

            if command == 'load' and args == None:
                try:
                    all_plugins = listdir('plugins')
                    not_loaded = []
                    for plugin in all_plugins:
                        if not plugin in self.__functions[0] and not (plugin.endswith('py') or plugin.endswith('pyc')) :
                            not_loaded.append(plugin)
                    self.notify(kwargs['from_nick'], 'Plugins not in use: ' + ", ".join(not_loaded) + '.')
                except Exception as e:
                    stderr.write(repr(e) + "\n")
                    self.notify(kwargs['from_nick'], 'Error: plugin directory not found.')

            if command == 'unload' and args == None:
                self.notify(kwargs['from_nick'], 'Plugins in use: ' + ', '.join(self.__functions[0]) + '.')
                    
        super(PluginBot, self).cmd(command, args, channel, **kwargs)
        for name, obj, attr in zip(self.__functions[0], self.__functions[1], self.__functions[2]):
            if attr:
                try:
                    self._send_message(obj.cmd(command, args, channel, **kwargs))
                except Exception as e:
                    stderr.write("Plugin {p} gave error {ex}\n".format(p=name, ex = e))
                    self.__unload_plugin(name)
                    self.msg(channel, "Plugin {p} gave an error and has been unloaded.".format(p = name),
                             to=kwargs['from_nick'])
                
        if DEBUG: stderr.write("PluginBot CMD\n")

    def listen(self, command, msg, channel, **kwargs):
        if DEBUG: stderr.write("PluginBot Listen begin\n")
        for name, obj, attr, blacklist in zip(self.__functions[0], self.__functions[1], self.__functions[3], self.__functions[6]):
            if attr:
                if len(blacklist) > 0 and channel in blacklist: continue 
                try:
                    self._send_message(obj.listen(msg, channel, **kwargs))
                except Exception as e:
                    stderr.write(err, "Plugin {p} gave error {ex}\n".format(p=name, ex = e))
                    self.__unload_plugin(name)
                    self.msg(channel, "Plugin {p} gave an error and has been unloaded.".format(p = name),
                             to=kwargs['from_nick'])
                    
        super(PluginBot, self).listen(command, msg, channel, **kwargs)
        if DEBUG: stderr.write("PluginBot Listen end\n")

    def help(self, command, args, channel, **kwargs):
        if DEBUG: stderr.write("PluginBot Help begin\n")

        if command == 'all':
            self.notify(kwargs['from_nick'], 'PluginBot: load, unload, reload, forceunload, blacklist')
        elif command == 'load':
            self.notify(kwargs['from_nick'], '!load [name]')
            self.notify(kwargs['from_nick'], 'Will load plugin with [name], else it will show a list of plugins not loaded.')
        elif command == 'unload':
            self.notify(kwargs['from_nick'], '!unload [name]')
            self.notify(kwargs['from_nick'], 'Will unload plugin with [name], else it will show a list of plugins loaded.')
        elif command == 'reload':
            self.notify(kwargs['from_nick'], '!reload name')
            self.notify(kwargs['from_nick'], 'Reload plugin with name. Plugin must be loaded for this to work')
        elif command == 'forceunload':
            self.notify(kwargs['from_nick'], '!forceunload name')
            self.notify(kwargs['from_nick'], 'Will purge a plugin from the system. Only available to admins with level 98 and up.')
            
        for name, obj, attr in zip(self.__functions[0], self.__functions[1], self.__functions[4]):
            if attr: 
                try:
                    self._send_message(obj.help(command, args, channel, **kwargs))
                except Exception as e:
                    sys.stderr.write("Plugin {p} gave error {ex}\n".format(p=name, ex = e))
                    self.__unload_plugin(name)
                    self.msg(channel, "Plugin {p} gave an error and has been unloaded.".format(p = name),
                             to=kwargs['from_nick'])
                    
        super(PluginBot, self).help(command, args, channel, **kwargs)
        if DEBUG: stderr.write("PluginBot Help end\n")
