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
            if IRC_DEBUG:
                print("""
                ::::::::::::: WARNING :::::::::::::::: 
                The IRC_DEBUG option is ON in the current
                configuration. This will cause passwords to
                come up in plaintext in your terminal. This 
                is not recommended for any other use other
                than debugging!""")

            secret = raw_input('SECRET:')
            self.authsys = AuthSys(secret)
            self.nick_user_relation = {}
            self.user_nick_relation = {}
            if RECOVER_USERS:
                self.authsys.recover_users()
        
    def cmd(self, command, args, channel, **kwargs):
        if DEBUG: print("Authentication Bot Command")
        if AUTHENTICATION:
            kwargs['auth_nick'], kwargs['auth_level'] = self.authsys.online_info("{u}@{h}".format(u = kwargs['from_ident'], h =  kwargs['from_host_mask']))
            if command == 'register':
                args = args.split()
                if IRC_DEBUG: self.notify(kwargs['from_nick'], "WARNING: IRC_DEBUG is ON. This means the admin can see your password in plaintext")
                if len(args) == 2:
                    result = self.authsys.add(args[0], args[1])
                    if result: self.msg(channel, result, to=kwargs['from_nick'])
                    else: self.msg(channel, "Email sendt to {u}.".format(u = args[1]), to=kwargs['from_nick'])

            elif command == 'setpass':
                args = args.split()
                if IRC_DEBUG: self.notify(kwargs['from_nick'], "WARNING: IRC_DEBUG is ON. This means the admin can see your password in plaintext")
                if len(args) == 3:
                    result = self.authsys.setpass(args[0], args[1], args[2])
                    if result: self.msg(channel, "Password updated", to=kwargs['from_nick'])
                    else: self.msg(channel, "Cookie not correct!", to=kwargs['from_nick'])

            elif command == 'login':
                args = args.split()
                if IRC_DEBUG: self.notify(kwargs['from_nick'], "WARNING: IRC_DEBUG is ON. This means the admin can see your password in plaintext")
                if len(args) == 2:
                    result = self.authsys.login(
                        args[0], args[1], 
                        "{i}@{h}".format(i = kwargs['from_ident'], 
                                         h = kwargs['from_host_mask']))
                    if result: 
                        self.nick_user_relation[kwargs['from_nick']] = args[0]
                        self.user_nick_relation[args[0]] = kwargs['from_nick']
                        self.msg(channel, "Logged in!", to=kwargs['from_nick'])
                    else: self.msg(channel, "Wrong pass!", to=kwargs['from_nick'])

            elif command == 'online':
                result = self.authsys.is_online(args)
                if result: self.msg(channel, "He is online!", to=kwargs['from_nick'])
                else: self.msg(channel, "He is not online!", to=kwargs['from_nick'])

            elif command == 'chlvl' or command == 'changelevel':
                args = args.split()
                nick, level = (args[0], int(args[1]))
                self.authsys.change_level(nick, level,
                                          "{u}@{h}".format(u = kwargs['from_ident'], 
                                                           h =  kwargs['from_host_mask']))
                
            else:
                # :::: IMPORTANT NOTE ::::
                # NO AUTHENTICATION COMMAND SHOULD BE
                # PASSED DOWN THE CHAIN. IT SHOULD NOT
                # BE LOGGED AT ANY TIME AND IT SHOULD
                # NEVER BE NECCESARY TO DO POST-PROCESSING
                # ON THESE COMMANDS.
                kwargs['nick_to_user'] = self.nick_user_relation
                kwargs['user_to_nick'] = self.user_nick_relation
                if DEBUG: print("NICK TO USER RELATION DICTIONARY: " + str(self.nick_user_relation) + str(self.user_nick_relation))
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
            if kwargs['from_nick'] in self.nick_user_relation: del(self.nick_user_relation[kwargs['from_nick']])
        if command == "PART" and not self.visible_for_bot(kwargs['from_nick']):
            self.authsys.logout("{i}@{h}".format(i = kwargs['from_ident'], h = kwargs['from_host_mask']))
            if kwargs['from_nick'] in self.nick_user_relation: del(self.nick_user_relation[kwargs['from_nick']])
        if command == "NICK":
            if kwargs['from_nick'] in self.nick_user_relation:
                self.nick_user_relation[kwargs['msg']] = self.nick_user_relation[kwargs['from_nick']]
                del(self.nick_user_relation[kwargs['from_nick']])
