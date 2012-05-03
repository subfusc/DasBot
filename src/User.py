#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Skrevet av Sindre Wetjen
import hashlib
import os
import smtplib
import random
from email.mime.text import MIMEText
from GlobalConfig import *

class User:
    
    def __init__(self, nick, email, secret, level = 0):
        self.nick = nick
        self.email = email
        self.lin = False
        self.domain = None
        self.level = level
        self.cookie = "lolimon"
        print email
        msg = MIMEText('''hi %s
your cookie is %s
''' % (nick, self.cookie))

        msg['Subject'] = "Bot registration for %s" % nick
        msg['From'] = BOT_EMAIL
        msg['To'] = email

        s = smtplib.SMTP('smtp.uio.no')
        s.sendmail(BOT_EMAIL, [email], msg.as_string())
        s.close()
        
    def online(self, domain):
        return self.lin and self.domain == domain

    def get_level(self):
        return self.level

    def check_password(self, string, secret):
        check = hashlib.sha256()
        check.update(string + secret)

        for x in range(0, HASH_ROUNDS):
            check.digest()

        password = self.password.copy()
        return password.digest() == check.digest()

    def login(self, password, domain, secret):
        if self.check_password(password, secret) and not self.lin:
            self.lin = True
            self.domain = domain
            return True
        return False

    def logout(self):
        self.lin = False
        self.domain = None

    def make_pass(self, cookie, passw, secret):
        if cooke == self.cookie:
            self.password = hashlib.sha256()
            self.password.update(passw + secret)
            
            for x in range(0, HASH_ROUNDS):
                self.password.digest()
        
    def change_pass(self, oldpass, newpass, secret):
        if check_password(self, oldpass, secret):
            self.password = hashlib.sha256()
            self.password.update(newpass + secret)
            
            for x in range(0, HASH_ROUNDS):
                self.password.digest()


if __name__ == "__main__":
    usr = User("SINDRE", "HALLABALLA")
    print usr.password
    print usr.check_password("HALLABALLA")
    print usr.check_password("ZOMGIMONOS")
    print usr.check_password("HALLABALLA")
