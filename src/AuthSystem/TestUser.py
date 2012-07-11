#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Written by Sindre Wetjen
# Distributed under a GPLv3 License
# See the LICENSE file in the top directory
# for full agreement.
from User import User

EMAIL_TESTS = False
SECRET = "secret"

def test_creation():
    a = User("Admin", "admin@test.com", level = 100)
    u = User("Nick", "user@test.com") 
    passed = a.nick == "Admin" and u.nick == "Nick"
    passed &= a.email == "admin@test.com" and u.email == "user@test.com"
    passed &= a.level == 100 and u.level == 0
    passed &= a.password == None and u.password == None
    print("User Creation Test: [ "),
    print("PASSED ]" if passed else "FAILED ]")
    return (a,u)

def test_password(a, u):
    a.make_pass(a.cookie, "adminPass", SECRET)
    u.make_pass(u.cookie, "userPass", SECRET)
    passed = a.password != "adminPass" and u.password != "userPass"
    passed &= a.check_password("adminPass", SECRET) and u.check_password("userPass", SECRET)
    passed &= not (a.check_password("userPass", SECRET) or u.check_password("adminPass", SECRET))
    passed &= not a.check_password(None, None) and not u.check_password(None, None)
    print("User Password Test: [ " + ("PASSED" if passed else "FAILED") + " ]")
    return passed
    
def test_login(a, u):
    adomain = "admin@administan.dw"
    udomain = "user@useristan.dw"
    passed = not (a.online(adomain) and 
                u.online(udomain))
    passed &= not (a.login("userPass", adomain, SECRET) and 
                u.login("adminPass", udomain, SECRET))
    passed &= (a.login("adminPass", adomain, SECRET) and
               u.login("userPass", udomain, SECRET))
    passed &= a.online(adomain) and u.online(udomain)
    print("User Login Test: [ " + ("PASSED" if passed else "FAILED") + " ]")
    return passed
    
def test_logout(a, u): 
    adomain = "admin@administan.dw"
    udomain = "user@useristan.dw"
    passed = a.online(adomain) and u.online(udomain)
    a.logout()
    u.logout()
    passed &= not (a.online(adomain) and u.online(udomain))
    print("User Logout Test: [ " + ("PASSED" if passed else "FAILED") + " ]")
    return passed
    
def test_level(a, u):
    passed = a.level == 100 and u.level == 0
    print("User Level Test: [ " + ("PASSED" if passed else "FAILED") + " ]")
    return passed
    
def test_edit(a, u): 
    adomain = "admin@administan.dw"
    udomain = "user@useristan.dw"
    passed = not(a.change_pass("jokepass","newapass", SECRET) and
                 u.change_pass("anotherjokepass", "newupass", SECRET))
    passed &= not(a.login("newapass", adomain, SECRET) and 
                  u.login("newupass", udomain, SECRET))
    passed &= (a.change_pass("adminPass", "newapass", SECRET) and 
               u.change_pass("userPass", "newupass", SECRET))
    passed &= (a.login("newapass", adomain, SECRET) and 
               u.login("newupass", udomain, SECRET))
    print("User Edit Test: [ " + ("PASSED" if passed else "FAILED") + " ]")
    return passed
    
def test_user():
    a,u = test_creation()
    passed = True if u and a else False
    passed &= test_password(a, u)
    passed &= test_login(a, u)
    passed &= test_logout(a, u)
    passed &= test_edit(a, u)
    print("All User Tests: [ " + ("PASSED" if passed else "FAILED") + " ]")

if __name__ == '__main__':
    test_user()
