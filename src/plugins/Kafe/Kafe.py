# -*- coding: utf-8 -*-
import urllib2
import time
import re
import json

class Kafe(object):
    
    def __init__(self, cafename):
        self.cafename = cafename
        self.url = 'http://dagensmiddag.net/index.json'
        self.response = urllib2.urlopen(self.url)
        self.middager = json.load(self.response)
        self.weekday = time.localtime().tm_wday
        for cafe in self.middager['cafes']:
            if cafe['name'] == self.cafename:
                self.menu = cafe['menu']
                self.opening_hours = cafe['open']
    
    def todaysDinner(self):
        if self.opening_hours[self.weekday] == u'Stengt':
            return [u"Kafeen er stengt"]
        else:
            tmp = list()
            for dt in self.menu[self.weekday]:
                for j in self.menu[self.weekday][dt]:
                    tmpstr = j.replace("     ", " ").strip(",").encode('utf-8')
                    tmp.append(tmpstr)
            return tmp

if __name__ == "__main__":
    test = Kafe('Informatikkafeen')
    print test.todaysDinner()
