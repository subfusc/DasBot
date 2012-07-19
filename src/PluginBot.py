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
from ChannelManagerBot import ChannelManagementBot
import sys
from GlobalConfig import *

class PluginBot(ChannelManagementBot):

    def __init__(self):
        super(PluginBot, self).__init__()
        self.__plugins = None
        self.__functions = [[], [], [], [], []]
        if 'LOAD_PLUGINS' in locals() or 'LOAD_PLUGINS' in globals() and isinstance(LOAD_PLUGINS, list):
            for plugin in LOAD_PLUGINS:
                self.__load_plugin(plugin)

    def _send_message(self, message_array):
        if message_array == None: return
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
            return True
        except Exception as e:
            print(e)
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
            self.__system_unload(name)
            del(self.__functions[0][index])
            del(self.__functions[1][index])
            del(self.__functions[2][index])
            del(self.__functions[3][index])
            del(self.__functions[4][index])
            return True
        except Exception as e:
            print(e)
            return False
            
    def cmd(self, command, args, channel, **kwargs):
        if DEBUG: print("PluginBot CMD")
        if kwargs['auth_level'] >= 90:
            if command == "load":
                if self.__has_plugin(args): 
                    self.msg(channel, "Plugin \"" + args + "\" is allready loaded!", to = kwargs['from_nick'])
                elif self.__load_plugin(args):
                    self.msg(channel, "Plugin \"" + args + "\" is now loaded.", to = kwargs['from_nick'])
                else: self.msg(channel, "Plugin \"" + args + "\" could not be loaded.", to = kwargs['from_nick'])
            elif command == "unload":
                if self.__unload_plugin(args):
                    self.msg(channel, "Plugin \"" + args + "\" is now unloaded.", to = kwargs['from_nick'])
                else: self.msg(channel, "Plugin \"" + name + "\" is not loaded.", to = kwargs['from_nick'])
            elif command == "reload":
                if self.__unload_plugin(args) and self.__load_plugin(args):
                    self.msg(channel, "Plugin \"" + args + "\" is now reloaded.", to = kwargs['from_nick'])
                else:
                    self.msg(channel, "Plugin \"" + args + "\" gave an error while reloading.", to = kwargs['from_nick'])
        if kwargs['auth_level'] >= 95:
            if command == "forceunload":
                self.__system_unload(args)

        super(PluginBot, self).cmd(command, args, channel, **kwargs)
        for name, obj, attr in zip(self.__functions[0], self.__functions[1], self.__functions[2]):
            if attr:
                try:
                    self._send_message(obj.cmd(command, args, channel, **kwargs))
                except Exception as e:
                    print("Plugin {p} gave error {ex}".format(p=name, ex = e))
                    self.__unload_plugin(name)
                    self.msg(channel, "Plugin {p} gave an error and has been unloaded.", to=kwargs['from_nick'])
                
        if DEBUG: print("PluginBot CMD")

    def listen(self, command, msg, channel, **kwargs):
        if DEBUG: print("PluginBot Listen begin")
        for name, obj, attr in zip(self.__functions[0], self.__functions[1], self.__functions[3]):
            if attr: 
                try:
                    self._send_message(obj.listen(msg, channel, **kwargs))
                except Exception as e:
                    print("Plugin {p} gave error {ex}".format(p=name, ex = e))
                    self.__unload_plugin(name)
                    self.msg(channel, "Plugin {p} gave an error and has been unloaded.", to=kwargs['from_nick'])
                    
        super(PluginBot, self).listen(command, msg, channel, **kwargs)
        if DEBUG: print("PluginBot Listen end")

    def help(self, command, args, channel, **kwargs):
        if DEBUG: print("PluginBot Help begin")
        for name, obj, attr in zip(self.__functions[0], self.__functions[1], self.__functions[4]):
            if attr: 
                try:
                    self._send_message(obj.help(command, args, channel, **kwargs))
                except Exception as e:
                    print("Plugin {p} gave error {ex}".format(p=name, ex = e))
                    self.__unload_plugin(name)
                    self.msg(channel, "Plugin {p} gave an error and has been unloaded.", to=kwargs['from_nick'])
                    
        super(PluginBot, self).help(command, args, channel, **kwargs)
        if DEBUG: print("PluginBot Help end")
