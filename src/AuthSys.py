#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Skrevet av Sindre Wetjen
from User import User

class AuthSys:

    def __init__(self):
        self.userlist = {}
        self.domainlist = {}
        nick = raw_input("NICK: ")
        passwd = raw_input("PASS: ")
        self.add(nick, passwd, "a")

    def add(self, nick, passwd, level = "n"):
        self.userlist[nick] = User(nick, passwd, level)
        
    def login(self, nick, passwd, domain):
        if (nick in self.userlist) and self.userlist[nick].login(passwd, domain):
            self.domainlist[domain] = self.userlist[nick]
            return True
        return False

    def online(self, domain):
        return domain in self.domainlist
    
    def level(self, domain):
        if domain in self.domainlist:
           return self.domainlist[domain].get_level()

    def list_users(self):
        return str(self.userlist.keys())

    def logout(self, domain):
        if domain in self.domainlist:
            self.domainlist[domain].logout()
            del self.domainlist[domain]
