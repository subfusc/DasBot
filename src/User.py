#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Skrevet av Sindre Wetjen
import hashlib

class User:
    
    def __init__(self, nick, password, level = "n"):
        self.nick = nick
        self.password = hashlib.sha256()
        self.password.update(password)
        self.lin = False
        self.domain = None
        self.level = level

        for x in range(0, 20):
            self.password.digest()
        
    def online(self, domain):
        return self.lin and self.domain == domain

    def get_level(self):
        return self.level

    def check_password(self, string):
        check = hashlib.sha256()
        check.update(string)

        for x in range(0, 20):
            check.digest()

        password = self.password.copy()
        return password.digest() == check.digest()

    def login(self, password, domain):
        if self.check_password(password) and not self.lin:
            self.lin = True
            self.domain = domain
            return True
        return False

    def logout(self):
        self.lin = False
        self.domain = None

    def change_pass(self, oldpass, newpass):
        if check_password(self, oldpass):
            self.password = haslib.sha256()
            self.password.update(newpass)
            
            for x in range(0, 20):
                self.password.digest()


if __name__ == "__main__":
    usr = User("SINDRE", "HALLABALLA")
    print usr.password
    print usr.check_password("HALLABALLA")
    print usr.check_password("ZOMGIMONOS")
    print usr.check_password("HALLABALLA")
