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
        super(AuthBot, self).__init__()

    def stop(self):
        super(AuthBot, self).stop()
        self.authsys.stop()
        del(self.authsys)
        
    def cmd(self, command, args, channel, **kwargs):
        if DEBUG: print("Authentication Bot Command")
        if AUTHENTICATION:
            kwargs['auth_nick'], kwargs['auth_level'] = self.authsys.online_info("{u}@{h}".format(u = kwargs['from_ident'], h =  kwargs['from_host_mask']))
            if command == 'register':
                args = args.split()
                if IRC_DEBUG: self.notify(kwargs['from_nick'], "WARNING: IRC_DEBUG is ON. This means the admin can see your password in plaintext")
                if len(args) == 2:
                    result = self.authsys.add(args[0], args[1])
                    if result: self.notify(kwargs['from_nick'], result)
                    else: self.notify(kwargs['from_nick'], "Email sendt to {u}.".format(u = args[1]))

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
                        self.notify(kwargs['from_nick'], "Logged in!")
                    else: self.notify(kwargs['from_nick'], "Wrong pass!")

            elif command == 'logout':
                self.authsys.logout("{i}@{h}".format(i = kwargs['from_ident'], h = kwargs['from_host_mask']))
                if kwargs['from_nick'] in self.nick_user_relation: del(self.nick_user_relation[kwargs['from_nick']])
                if kwargs['from_nick'] in self.user_nick_relation: del(self.user_nick_relation[kwargs['from_nick']])

            elif command == 'online':
                result = None
                if args == None: 
                    if kwargs['from_nick'] in self.nick_user_relation:
                        result = self.authsys.is_online(self.nick_user_relation[kwargs['from_nick']])
                else:
                    if args[0] == '*':
                        result = self.authsys.is_online(args[1:])
                    else:
                        if args in self.nick_user_relation:
                            result = self.authsys.is_online(self.nick_user_relation[args])
                if result: self.msg(channel, "(S)he is online!", to=kwargs['from_nick'])
                else: self.msg(channel, "(S)he is not online!", to=kwargs['from_nick'])

            elif (command == 'chlvl' or command == 'changelevel') and args:
                args = args.split()
                nick, level = (args[0], int(args[1]))
                if nick[0] == '*':
                    self.authsys.change_level(nick[1:], level,
                                              "{u}@{h}".format(u = kwargs['from_ident'], 
                                                               h =  kwargs['from_host_mask']))
                else:
                    if nick in self.nick_user_relation:
                        self.authsys.change_level(self.nick_user_relation[nick], level,
                                                  "{u}@{h}".format(u = kwargs['from_ident'], 
                                                                   h =  kwargs['from_host_mask']))
            elif command == 'resetpass':
                if args:
                    self.authsys.resetpass(args)

            elif command == 'listusers' and args and args[0] == 'verbose' and kwargs['auth_level'] >= 95:
                self.notify(kwargs['from_nick'], '== List of all users == ')
                for user in self.authsys.list_all_users():
                    self.notify(kwargs['from_nick'], user)

            elif command == 'listusers' or command == 'lusers':
                self.notify(kwargs['from_nick'], 'Users: {l}.'.format(l = ", ".join([self.user_nick_relation[nick] if nick\
                                                                                     in self.user_nick_relation else "*" + nick\
                                                                                     for nick in self.authsys.list_users()])))

            elif command == 'listonline' or command == 'lonline':
                self.notify(kwargs['from_nick'], 'Online: {l}.'.format(l = " ,".join([self.user_nick_relation[nick] for nick in self.authsys.get_online()])))

            elif command == 'lvl' or command == 'level':
                if args:
                    if args[0] == '*': self.notify(kwargs['from_nick'], str(self.authsys.get_level(args[1:])))
                    else:
                        if args in self.nick_user_relation: 
                            self.notify(kwargs['from_nick'], str(self.authsys.get_level(self.nick_user_relation[args])))
                else:
                    if kwargs['from_nick'] in self.nick_user_relation:
                        self.notify(kwargs['from_nick'], str(self.authsys.get_level(self.nick_user_relation[kwargs['from_nick']]))) 

            elif command == 'whois':
                nick = kwargs['from_nick'] if args == None else args
                self.notify(kwargs['from_nick'], "(S)he is {n}".format(n = 'no one.' if not nick in self.nick_user_relation else (self.nick_user_relation[nick] + ".")))
                
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

    def help(self, command, args, channel, **kwargs):
        super(AuthBot, self).help(command, args, channel, **kwargs)
        if command == 'register':
            self.notify(kwargs['from_nick'], "!register <nick> <email>")
            self.notify(kwargs['from_nick'], "This will register a nick with an email in the bots user")
            self.notify(kwargs['from_nick'], "database. Please follow the email instructions to set a ")
            self.notify(kwargs['from_nick'], "password.")
        elif command == 'login':
            self.notify(kwargs['from_nick'], "!login <nick> <password>")
            self.notify(kwargs['from_nick'], "Log in to an account using your registered nick and password")
        elif command == 'setpass':
            self.notify(kwargs['from_nick'], "!setpass <nick> <cookie> <password>")
            self.notify(kwargs['from_nick'], "Set the password for nick with a cookie that will be sendt to")
            self.notify(kwargs['from_nick'], "your email.")
        elif command == 'chlvl' or command == 'changelevel':
            self.notify(kwargs['from_nick'], '!chlvl <user> <lvl>')
            self.notify(kwargs['from_nick'], 'Change the autorisation level of a given user. You have to have')
            self.notify(kwargs['from_nick'], 'higher authorisation than the level you are giving.')
        elif command == 'online':
            self.notify(kwargs['from_nick'], '!online [user] - Tells you if a user is online (defaults to self).')
        elif command == 'logout':
            self.notify(kwargs['from_nick'], '!logout')
            self.notify(kwargs['from_nick'], 'Log out from the autentication system of the bot')
        elif command == 'resetpass':
            self.notify(kwargs['from_nick'], '!resetpass <user>')
            self.notify(kwargs['from_nick'], 'Sends a new cookie to the users email, so that (s)he may change')
            self.notify(kwargs['from_nick'], 'the password')
        elif command == 'listonline' or command == 'lonline':
            self.notify(kwargs['from_nick'], '!lonline - List users logged into the bot system')
        elif command == 'lusers' or command == 'listusers':
            self.notify(kwargs['from_nick'], '!lusers - List users registered in the bot. * denotes that the user')
            self.notify(kwargs['from_nick'], 'is not online and this is the user account name')
        elif command == 'whois':
            self.notify(kwargs['from_nick'], '!whois [user] - Tells who a person is logged in as (default to one self).')
        elif command == 'lvl' or command == 'level':
            self.notify(kwargs['from_nick'], '!lvl [user] - Tells which authorization a user has (defaults to one self).')
        elif command == 'all':
            self.notify(kwargs['from_nick'], "AuthBot: login, setpass, chlvl, changelevel, online, register, logout, resetpass")
            self.notify(kwargs['from_nick'], "AuthBot: listonline, lonline, listusers, lusers, whois, lvl, level")
        
    def management_cmd(self, command, args, **kwargs):
        super(AuthBot, self).management_cmd(command, args, **kwargs)
        if command == "QUIT":
            self.authsys.logout("{i}@{h}".format(i = kwargs['from_ident'], h = kwargs['from_host_mask']))
            if kwargs['from_nick'] in self.nick_user_relation: del(self.nick_user_relation[kwargs['from_nick']])
            if kwargs['from_nick'] in self.user_nick_relation: del(self.user_nick_relation[kwargs['from_nick']])
        if command == "PART" and not self.visible_for_bot(kwargs['from_nick']):
            self.authsys.logout("{i}@{h}".format(i = kwargs['from_ident'], h = kwargs['from_host_mask']))
            if kwargs['from_nick'] in self.nick_user_relation: del(self.nick_user_relation[kwargs['from_nick']])
            if kwargs['from_nick'] in self.user_nick_relation: del(self.user_nick_relation[kwargs['from_nick']])
        if command == "NICK":
            if kwargs['from_nick'] in self.nick_user_relation:
                self.nick_user_relation[kwargs['msg']] = self.nick_user_relation[kwargs['from_nick']]
                del(self.nick_user_relation[kwargs['from_nick']])
            if kwargs['from_nick'] in self.user_nick_relation:
                self.user_nick_relation[kwargs['msg']] = self.user_nick_relation[kwargs['from_nick']]
                del(self.user_nick_relation[kwargs['from_nick']])
   
