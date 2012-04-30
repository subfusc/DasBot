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
        self.opnhrsless = self.opening_hours[self.weekday].split("-")[0].replace(":", "")
        self.opnhrsmore = self.opening_hours[self.weekday].split("-")[1].replace(":", "")
        self.currenthr = time.localtime().tm_hour + time.localtime().tm_min
    
    def todaysDinner(self):
        if self.opening_hours[self.weekday] == u'Stengt':
            return [u"Kafeen er stengt"]
        elif self.opnhrsless > self.currenthr or self.opnhrsmore < self.currenthr:
            return [u"Kafeen er stengt", u"Åpningstidene er " + self.opening_hours[self.weekday]]
        else:
            tmp = list()
            for dt in self.menu[self.weekday]:
                for j in self.menu[self.weekday][dt]:
                    tmpstr = j.replace("     ", " ").encode('utf-8')
                    tmp.append(tmpstr)
                    return tmp
