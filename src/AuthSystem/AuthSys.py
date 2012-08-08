#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Skrevet av Sindre Wetjen
from User import User
from AuthConfig import *
import sqlite3
import threading

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
        self.timers = []

    def __del__(self):
        if DEBUG: print("AUTH SYS DELETE CALLED")
        self.db.close()
        for t in self.timers:
            t.cancel()
        
    def stop(self):
        self.db.close()
        for t in self.timers:
            t.cancel()
        
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
                t = threading.Timer(24 * 60 * 60, timed_delete_user, [self, nick])
                t.start()
                self.timers.append(t)
            else:
                if not x == 0:
                    return "That email is already registered. Please use another one."
                elif nick in self.userlist:
                    return "That username is taken. Please try another username"
        except Exception as e:
            print e
            return "I got an error in registering. Please try again."

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

    def get_level(self, nick):
        if nick in self.userlist:
            return self.userlist[nick].get_level()
        else: return -1
        
    def is_online(self, nick):
        if nick in self.userlist:
            return self.userlist[nick].is_online()

    def list_users(self):
        return self.userlist.keys()

    def get_online(self):
        return [user.get_nick() for user in self.domainlist.values()]
    
    def list_all_users(self):
        string = ["{:<15} :: Auth level".format('Account')]
        for user in self.userlist.values():
            string.append('{:<15} :: {:>4}'.format(user.get_nick(), user.get_level()))
        return string
    
    def resetpass(self, nick):
        if nick in self.userlist:
            user = self.userlist[nick]
            user.reset_pass()

    def online_info(self, domain):
        if self.online(domain):
            user = self.domainlist[domain]
            if user.is_online(): return (user.get_nick(), user.get_level())
        return (None, 0) 

    def change_level(self, nick, level, domain):
        if self.online(domain):
            admin = self.domainlist[domain]
            if admin.get_level() > level and nick in self.userlist \
              and self.userlist[nick].get_level() < admin.get_level():
                user = self.userlist[nick]
                self.delete_user(nick)
                user.level = level
                self.userlist[user.get_nick()] = user
                user.put_in_sqlite3_database(self.db)
                
    def setpass(self, nick, cookie, passwd):
        if nick in self.userlist:
            result = self.userlist[nick].make_pass(cookie, passwd, self.secret)
            if result: 
                self.db.execute("DELETE FROM users WHERE nick = ?", [nick])
                self.userlist[nick].put_in_sqlite3_database(self.db)
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
