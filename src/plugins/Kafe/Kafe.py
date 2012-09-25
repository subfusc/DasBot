# -*- coding: utf-8 -*-
import urllib2
import time
import re
import json

class Kafe(object):
    
    def __init__(self, cafename):
        self.cafename = cafename.lower()
        self.url = 'http://dagensmiddag.net/index.json'
        self.update_offers()

    def update_offers(self):
        response = urllib2.urlopen(self.url)
        middager = json.load(response)
        self.week = int(time.strftime('%W'))
        self.weekday = int(time.strftime('%w'))
        self.db = [middager['week'], {}]
        kafeer = self.db[1]
        for cafe in middager['cafes']:
            name = cafe['name'].lower()
            kafeer[name] = {'open':self.__parse_time(cafe['open']),
                            'menu':self.__parse_menu(cafe['menu'], cafe['name'])}

    def __parse_theology(self, menu):
        tmparr = []
        for day in menu:
            for value in day.values():
                tmparr += value

        actualarr = []
        x = 0
        while x < len(tmparr):
            actualarr.append([('Dagens', tmparr[x + 0].replace('Dagens:     ', '')), 
                              ('Vegetar', tmparr[x + 1].replace('Dagens:     ', ''))])
            x += 3
            
        return actualarr
            
    def __parse_menu(self, menu, kafe):
        rarr = []
        # if kafe.startswith('Kaf'):
        #     rarr = self.__parse_theology(menu)
        # else:
        for day in menu:
            dayrarr = []
            for key in day:
                if type(day[key]) == list:
                    dayrarr.append((key, " || ".join(day[key])))
                else:
                    dayrarr.append((key, day[key]))
            rarr.append(dayrarr)
        return rarr
        
    def __parse_time(self, tider):
        rarr = []
        for tid in tider:
            if tid == 'Stengt':
                rarr.append(tid)
            else:
                rarr.append(self.__parse_a_time(tid))
        return rarr

    def __parse_a_time(self, tid):
        return ((int(tid[0:2]),int(tid[3:5])), (int(tid[6:8]), int(tid[9:11])))

    def __compare_times(self, tid, db_tid):
        tid = (int(tid[0:2]), int(tid[2:4]))
        if tid[0] == db_tid[0][0]:
            return tid[1] > db_tid[0][1]
        if tid[0] == db_tid[1][0]:
            return tid[1] < db_tid[1][1]
        return (db_tid[0][0] < tid[0]) and (db_tid[1][0] > tid[0])
            
    def __stengt(self, tid, tb_tid):
        if type(tb_tid) == str:
            return True
        else:
            return self.__compare_times(tid, tb_tid)
                
    def todaysDinner(self, kafe, check_closing=True):
        if self.db[0] != self.week or self.weekday != int(time.strftime('%w')):
            self.update_offers()
        if kafe == None: kafe = self.cafename
        for key in self.db[1]:
            if key.startswith(kafe):
                kafe = key
                break;
        else:
            return (kafe, None)

        if kafe in self.db[1]: 
            if check_closing and not self.__stengt(time.strftime('%H%M'), self.db[1][kafe]['open'][self.weekday - 1]):
                return (kafe, "Stengt")
            else:
                return (kafe, self.db[1][kafe]['menu'][self.weekday - 1])

    def make_response(self, dictionary):
        rarr = []
        for t in dictionary:
            rarr.append((t, dictionary[t][0]))
        return rarr

if __name__ == "__main__":
    test = Kafe('inf')
    print test.todaysDinner(None)
    print test.todaysDinner(None, False)
    print test.todaysDinner('sv', False)
    print test.todaysDinner('fr', False)
    print test.todaysDinner('ka', False)
    #print test.db
