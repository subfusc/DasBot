#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Skrevet av Sindre Wetjen
from User import User
import sqlite3
import threading

DATABASE_NAME = 'user_database.sql'

def timed_delete_user(system, user_nick):
    if not system.registered_user(user_nick):
        system.delete_user(user_nick)

class AuthSys:

    def __init__(self, secret):        
        self.db = sqlite3.connect(DATABASE_NAME)
        self.db.execute("""CREATE TABLE IF NOT EXISTS users 
        (nick string, email string, date integer, level integer, password blob, 
        UNIQUE (nick, email), PRIMARY KEY (nick))""")
        self.db.commit()
        
        self.secret = secret
        self.userlist = {}
        self.domainlist = {}

    def recover_users(self): 
        for row in self.db.execute("SELECT * FROM users"):
            self.userlist[row[0]] = User(row[0], row[1],
                                         date = row[2],
                                         level = row[3], 
                                         password = str(row[4]))
        
    def add(self, nick, email, level = 0):
        try:
            if len(self.userlist.keys()) == 0: level = 100
            x = 0
            
            for row in self.db.execute("SELECT * FROM users WHERE email = ?", [email]):
                x += 1
            if x == 0 and (not nick in self.userlist):
                self.userlist[nick] = User(nick, email, level=level)
                threading.Timer(24 * 60 * 60, timed_delete_user, [self, nick])
        except Exception as e:
            print e
            return "I got an error in registering. Please try again"
        
    def login(self, nick, passwd, domain):
        if (nick in self.userlist) and self.userlist[nick].login(passwd, domain, self.secret):
            self.domainlist[domain] = self.userlist[nick]
            return True
        return False

    def online(self, domain):
        return domain in self.domainlist
    
    def level(self, domain):
        if domain in self.domainlist:
           return self.domainlist[domain].get_level()

    def is_online(self, nick):
        if nick in self.userlist:
            return self.userlist[nick].is_online()
        
    def list_users(self):
        return str(self.userlist.keys())

    def setpass(self, nick, cookie, passwd):
        if nick in self.userlist:
            result = self.userlist[nick].make_pass(cookie, passwd, self.secret)
            if result: self.userlist[nick].put_in_sqlite3_database(self.db)
            return result
        return False

    def delete_user(self, nick):
        self.db.execute("DELETE FROM users WHERE nick = ?", [nick])
        self.db.commit()
        if nick in self.userlist:
            del(self.userlist[nick])

    def registered_user(self, nick):
        return nick in self.userlist and \
        self.userlist[nick].password != None and \
        self.userlist[nick].cookie == None
    
    def logout(self, domain):
        if domain in self.domainlist:
            self.domainlist[domain].logout()
            del(self.domainlist[domain])
