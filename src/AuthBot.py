# -*- coding: utf-8 -*-

import LoggerBot
from AuthSystem.AuthSys import AuthSys
from GlobalConfig import *

class AuthBot(LoggerBot.LoggerBot):
    """
    This is a class where the IRCBot has an authentication system
    TODO: Use existing authentication mekanism
    """

    def __init__(self):
        super(AuthBot, self).__init__()
        if AUTHENTICATION:
            secret = raw_input('SECRET:')
            self.authsys = AuthSys(secret)
            if RECOVER_USERS:
                self.authsys.recover_users()
        
    def cmd(self, command, args, channel, **kwargs):
        if DEBUG: print("Authentication Bot Command")
        if AUTHENTICATION:
            kwargs['auth_nick'], kwargs['auth_level'] = self.authsys.online_info("{u}@{h}".format(u = kwargs['from_ident'], h =  kwargs['from_host_mask']))
            if command == 'register':
                args = args.split()
                if len(args) == 2:
                    result = self.authsys.add(args[0], args[1])
                    if result: self.msg(channel, result, to=kwargs['from_nick'])
                    else: self.msg(channel, "Email sendt to {u}.".format(u = args[1]), to=kwargs['from_nick'])

            elif command == 'setpass':
                args = args.split()
                if len(args) == 3:
                    result = self.authsys.setpass(args[0], args[1], args[2])
                    if result: self.msg(channel, "Password updated", to=kwargs['from_nick'])
                    else: self.msg(channel, "Cookie not correct!", to=kwargs['from_nick'])

            elif command == 'login':
                args = args.split()
                if len(args) == 2:
                    result = self.authsys.login(
                        args[0], args[1], 
                        "{i}@{h}".format(i = kwargs['from_ident'], 
                                         h = kwargs['from_host_mask']))
                    if result: self.msg(channel, "Logged in!", to=kwargs['from_nick'])
                    else: self.msg(channel, "Wrong pass!", to=kwargs['from_nick'])

            elif command == 'online':
                result = self.authsys.is_online(args)
                if result: self.msg(channel, "He is online!", to=kwargs['from_nick'])
                else: self.msg(channel, "He is not online!", to=kwargs['from_nick'])

            else:
                # :::: IMPORTANT NOTE ::::
                # NO AUTHENTICATION COMMAND SHOULD BE
                # PASSED DOWN THE CHAIN. IT SHOULD NOT
                # BE LOGGED AT ANY TIME AND IT SHOULD
                # NEVER BE NECCESARY TO DO POST-PROCESSING
                # ON THESE COMMANDS.
                super(AuthBot, self).cmd(command, args, channel, **kwargs)
        else:
            kwargs['auth_nick'], kwargs['auth_level'] = (None, 0)
            super(AuthBot, self).cmd(command, args, channel, **kwargs)
                
    def listen(self, command, msg, channel, **kwargs):
        super(AuthBot, self).listen(command, msg, channel, **kwargs)

    def management_cmd(self, command, args, **kwargs):
        super(AuthBot, self).management_cmd(command, args, **kwargs)
        if command == "QUIT":
            self.authsys.logout("{i}@{h}".format(i = kwargs['from_ident'], h = kwargs['from_host_mask']))
        if command == "PART" and not self.visible_for_bot(kwargs['from_nick']):
            self.authsys.logout("{i}@{h}".format(i = kwargs['from_ident'], h = kwargs['from_host_mask']))
