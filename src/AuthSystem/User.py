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
        
            if BOT_EMAIL != '':
                msg = MIMEText('''hi %s
                your cookie is %s.
                You have 24 hours to register.
                ''' % (nick, self.cookie))
                
                msg['Subject'] = "Bot registration for %s" % nick
                msg['From'] = BOT_EMAIL
                msg['To'] = email
                
                s = smtplib.SMTP('smtp.uio.no')
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

    def check_password(self, string, secret):
        if self.password == None: return False
        if string == None: return False
        check = hashlib.sha256()
        check.update(string + (secret if secret else ""))

        for x in range(0, HASH_ROUNDS):
            check.digest()
        return self.password == check.digest()

    def login(self, password, ident, secret):
        if self.check_password(password, secret):
            self.ident = ident
            return True
        return False

    def logout(self):
        self.ident = None
        
    def make_pass(self, cookie, passw, secret):
        if self.cookie != None and cookie == self.cookie:
            password = hashlib.sha256()
            password.update(passw + secret)
            
            for x in range(0, HASH_ROUNDS):
                password.digest()
            self.password = password.digest()
            self.cookie = None
            return True
        return False
    
    def change_pass(self, oldpass, newpass, secret):
        if self.check_password(oldpass, secret):
            password = hashlib.sha256()
            password.update(newpass + secret)
            
            for x in range(0, HASH_ROUNDS):
                password.digest()
            self.password = password.digest()
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
