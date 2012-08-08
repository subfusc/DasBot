#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Skrevet av Sindre Wetjen
import hashlib
import sqlite3
import os
import smtplib
import random
import string
import time
from email.mime.text import MIMEText
from AuthConfig import *

def create_cookie(length=12, chars=string.letters + string.digits): 
    return ''.join([random.choice(chars) for x in range(length)])

class User:

    def __init__(self, nick, email, date = time.time(), level = 0, password = None):
        self.nick = nick
        self.email = email
        self.ident = None
        self.level = level
        self.date = int(date)
        if password == None:
            self.password = None
            self.cookie = create_cookie()
            if DEBUG: print(self.cookie)
        
            if BOT_EMAIL != '':
                msg = '''Hi {u},
                Your cookie is {c}.
                To complete the registration use the following command:
                /msg {i} !setpass {c} <desired password>
                You have 24 hours to register.
                '''.format(u = nick, c = self.cookie, i = BOT_NICK)

                if IRC_DEBUG:
                    msg += """
                    WARNING: The admin of this bot has debuging turned on.
                    This means he can see your password in plain text
                    while you are registering or login in, in his terminal.
                    """
                
                MIMEText(msg)
                
                msg['Subject'] = "Bot registration for {u}".format(u = nick)
                msg['From'] = BOT_EMAIL
                msg['To'] = email
                
                s = smtplib.SMTP(SMTP_SERVER)
                s.sendmail(BOT_EMAIL, [email], msg.as_string())
                s.close()
        else:
            self.password = password
    
    def online(self, ident):
        return self.ident != None and self.ident == ident

    def is_online(self):
        return self.ident != None
    
    def get_level(self):
        return self.level

    def get_nick(self):
        return self.nick

    def __create_hash(self, string, secret):
        check = hashlib.sha256()
        check.update(str(self.date) + string + (secret if secret else "default"))
        
        for x in range(0, HASH_ROUNDS):
            check.digest()
        return check.digest()
            
    def check_password(self, string, secret):
        if self.password == None: return False
        if string == None: return False
        return self.password == self.__create_hash(string, secret)

    def login(self, password, ident, secret):
        if self.check_password(password, secret):
            self.ident = ident
            return True
        return False

    def logout(self):
        self.ident = None
        
    def make_pass(self, cookie, passw, secret):
        if self.cookie != None and cookie == self.cookie:
            self.password = self.__create_hash(passw, secret)
            self.cookie = None
            return True
        return False

    def reset_pass(self): 
            self.cookie = create_cookie()
            if DEBUG: print(self.cookie)
            
            if BOT_EMAIL != '':
                msg = MIMEText('''Hi {u},
                Your cookie is {c}.
                To change you password, use the following command:
                /msg {b} !reset {c} <newpass> 
                '''.format(u = nick, c = self.cookie, i = BOT_NICK))

                if IRC_DEBUG:
                    msg += """
                    WARNING: The admin of this bot has debuging turned on.
                    This means he can see your password in plain text
                    while you are registering or login in, in his terminal.
                    """
                
                msg['Subject'] = "Bot registration for {u}".format(u = nick)
                msg['From'] = BOT_EMAIL
                msg['To'] = email
                
                s = smtplib.SMTP(SMTP_SERVER)
                s.sendmail(BOT_EMAIL, [email], msg.as_string())
                s.close()
    
    def change_pass(self, passortoken, newpass, secret):
        if self.check_password(passortoken, secret) or (self.cookie != None and self.cookie == passortoken):
            self.password = self.__create_hash(newpass, secret)
            return True
        return False

    def put_in_sqlite3_database(self, database):
        try:
            if self.password != None:
                database.execute("""INSERT INTO users 
                (nick, email, date, level, password) VALUES (?,?,?,?,?)""", 
                [self.nick, self.email, self.date, self.level, sqlite3.Binary(self.password)])
                database.commit()
        except Exception as e:
            print(e)
            print("Error in trying to add user to database")
