# -*- coding: utf-8 -*-
# Backend for storing Karma and calculate karma in a given time t using Cosine.
# Copyright (C) 2012  Sindre Wetjen

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sqlite3
from math import cos, sin, pi
from time import time, sleep
from sys import stderr

DEBUG = False

class DatabaseIsNotOpenError(Exception): pass

class KosBackend(object):
    """
    Backend for calculating and storing karma for entities. It uses Cosine to
    calculate karma in a given time t, and is implementet with lazy delete.
    """

    def __init__(self, database_name=None, decay_time=60, lowercase=False):
        """
        Create an instance of the KosBackend which calculates karma using the
        cosinus function.
        
        @type database_name: string
        @param database_name: the location of the database to store karma
        @type decay_time: number
        @param decay_time: the number of days untill karma has expired
        @type lowercase: boolean
        @param lowercase: Whether or not the entities should be lowercased

        @rtype: KosBackend
        @return: A new instance of KosBacked
        """
        self.utable = "utable"
        self.decay_time = decay_time * 24 * 60 * 60 #: The calculated decay time
        self.sql_db = None #: the sql databse
        self.db_open = False #: tell that the database is open
        self.lowercase = lowercase #: should I attempt to lowercase? 
        self.connect(database_name=database_name)


    def __exe(self, string, values=None):
        if DEBUG: stderr.write((string + " " + str(values) if values else string + " --") + "\n")
        if values:
            return self.sql_db.execute(string, values)
        else:
            return self.sql_db.execute(string)
            
    def __com(self):
        self.sql_db.commit()

    def _calculate(self, x, t = None):
        return self._opTan(x, t)

    def _opSimple(self, x, t = None):
        if t == None: t = int(time())
        return 1 / (((t - x) + self.decay_time)/self.decay_time)

    def _cosCalculate(self, x, t = None):
        if t == None: t = int(time())
        # stderr.write("X: {x} T: {t} COSCALC: {c}\n".format(x = x, t = t,
        # c = cos((pi * (t - x)) / (2 * self.decay_time))))
        return cos((pi * (t - x)) / (2 * self.decay_time)) 

    def _opPropotional(self, x, t = None):
        if t == None: t = int(time())
        #3600/(x-(1/(3600*x))+3600))))
        return self.decay_time / ((t - x) - (1 / (((t - x)* self.decay_time)*((t - x)* self.decay_time)) ) + self.decay_time)

    def _opTan(self, x, t = None):
        if t == None: t = int(time())
        #((sin(-1.8/300*x*pi-10)/(cos(-1.8/300*x*pi-10)+1))+6)/10
        #((sin(-1.7/3000*x*pi+2.72)/(cos(-1.7/3000*x*pi+2.72)+1))+5)/10
        return ((sin(-1.7/self.decay_time*((t-x)*pi)+2.72)/(cos(-1.7/self.decay_time*((t-x)*pi)+2.72)+1))+5)/10

    def _opPropotionalAlt(self, x, t = None):
        if t == None: t = int(time())
        return 1/((t-x)-((t-x)/2)+2) # Mangler decay time
        
    def _addKarma(self, positive, entity):
        if self.db_open:
            user = self._checkUserOrCreateDatabase(entity)
            self.__exe("INSERT INTO {table} (positive, date) VALUES (?, ?)".format(table = ("user" + str(user))), 
                        (positive, int(time())))
        else:
            raise DatabaseIsNotOpenError('The database is not open')

    def _userExists(self, entity):
        if self.lowercase: entity.lower()
        r = self.__exe("SELECT * FROM {table} WHERE entity = ? ;".format(table = self.utable),
                       (entity.lower() if self.lowercase else entity, )).fetchone()
        # stderr.write(str(r) + "\n")
        return r[0] if r else False
        
    def _conditionalCreateOverview(self):
        self.__exe("CREATE TABLE IF NOT EXISTS " + self.utable
                   + " (id INTEGER PRIMARY KEY, entity TEXT UNIQUE NOT NULL);")
        self.__com()
        for row in self.__exe("SELECT * FROM " + self.utable + ";"):
            self.__exe("CREATE TABLE IF NOT EXISTS " + ("user" + str(row[0]))
                                + " (positive INTEGER, date INTEGER NOT NULL);")
        self.__com()
                
    def _checkUserOrCreateDatabase(self, entity):
        user = self._userExists(entity)
        if not user:
            self.__exe("INSERT INTO {table} (id, entity) VALUES (?, ?);".format(table = self.utable),
                       (None, entity.lower() if self.lowercase else entity))
            self.__com()
            user = self._userExists(entity)
            self.__exe("CREATE TABLE {table} (positive INTEGER, date INTEGER NOT NULL)".format(table = "user" + 
                                                                                               str(user)))
        return user

    def _delEntity(self, entity):
        user = self._userExists(entity)
        if user:
            self.__exe("DELETE FROM {table} WHERE id = ?;".format(table = self.utable), (user, ))
            self.__exe("DROP TABLE {table};".format(table = "user" + str(user)))
            self.__com()
        
    def connect(self, database_name=None):
        """
        Connect to a karma database. Note: Its not necessary to call this function
        if you gave a database_name to the constructor.

        @type database_name: string
        @param database_name: Path to the database.

        @rtype: None
        """
        if (database_name):
            self.sql_db = sqlite3.connect(database_name) if database_name else None
            self.db_open = True if self.sql_db else False
        
        if self.db_open:
            self._conditionalCreateOverview()
        else:
            raise DatabaseIsNotOpenError('The database is not open')

    def disconnect(self):
        """
        Clean up and Disconnect from the database. Call this before exiting to ensure
        that all changes are commited.

        @rtype: None
        """
        if self.db_open:
            self.sql_db.close()
            self.db_open = False
        
    def positiveKarma(self, entity):
        """
        Add a +1 karma to an entity

        @type entity: string
        @param entity: the entity that you want to give +1 to.

        @rtype: None
        """
        self._addKarma(1, entity)

    def negativeKarma(self, entity):
        """
        Add a -1 karma to an entity

        @type entity: string
        @param entity: the entity that you want to give +1 to.

        @rtype: None
        """
        self._addKarma(0, entity)

    def getAllEntities(self):
        """
        Return a list with all entities in the current Karma database.

        @rtype: list
        @return: List of entities
        """
        try:
            return [ row[1] for row in self.__exe("SELECT * FROM {table};".format(table = self.utable)) ]
        except Exception:
            return []
        
    def getKarma(self, entity, t = None, doNotDelete=False):
        """
        Calculate the karma of an entity at time t. If time is not given, the function will assume "now".

        If you want to calculate a top-list you should use a reference time t and pass it to the function
        in order to get an accurate time.

        @type entity: string
        @param entity: The entity you want to calculate current karma for
        @type t: integer
        @param t: the refference time. Now if none is given.
        @type doNotDelete: boolean
        @param doNotDelete: If you don't want stuff to be deleted when checking for a
        special time, set this to true!
        
        @rtype: touple
        @return: the karma of an entity, the number of positive and the number of negative.
        """
        if t == None: t = time()
        if not self.db_open: raise DatabaseIsNotOpenError('The database is not opened')
        user = self._userExists(entity)
        if user: 
            self.__com()
            if not doNotDelete: 
                self.__exe("DELETE FROM {table} WHERE date <= ?".format(table = ("user" + str(user))), 
                           (t - self.decay_time, ))
            karma = 0
            pos = 0
            neg = 0
            for row in self.__exe("SELECT * FROM {table}".format(table = "user" + str(user))):
                print(row[1])
                if row[0] == 1:
                    karma += self._calculate(row[1], t = t)
                    pos += 1
                else:
                    karma -= self._calculate(row[1], t = t)
                    neg += 1
            return (karma, pos, neg)
        return (0, 0, 0)

    def getNBestList(self, n=5, t=None):
        """
        Calculate the top N entities with karma for a given time T. T is default
        "now"

        @type n: integer
        @param n: The number of entities you want back
        @type t: integer
        @param t: The date you want calculated (unixtime)

        @rtype: list
        @return: A list of the N entities with the best karma inkl n/positive karma and n/negative karma.
        """
        rlist = []
        if not t: t = time()
        print(t, t - self.decay_time)
        for entity in self.getAllEntities():
            karma = self.getKarma(entity, t=t)
            if karma[1] == 0 and karma [2] == 0: 
                self._delEntity(entity)
                continue
            
            if len(rlist) < n:
                for large_entity, x in zip(rlist, range(0, len(rlist) + 1)):
                    if large_entity[1][0] <= karma[0]:
                        rlist.insert(x, (entity, karma))
                        break
                else: rlist.append((entity, karma))
            else:
                for large_entity, x in zip(rlist, range(0, len(rlist) + 1)):
                    if large_entity[1][0] <= karma[0]:
                        rlist.insert(x, (entity, karma))
                        rlist.pop()
                        break
        return rlist
                
    def getNWorstList(self, n=5, t=None):
        """
        Calculate the bottom N entities with karma for a given time T. T is default
        "now"

        @type n: integer
        @param n: The number of entities you want back
        @type t: integer
        @param t: The date you want calculated (unixtime)

        @rtype: list
        @return: A list of the N entities with the worst karma inkl n/positive karma and n/negative karma.
        """
        
        rlist = []
        if not t: t = time()
        for entity in self.getAllEntities():
            karma = self.getKarma(entity,t=t)
            if karma[1] == 0 and karma[2] == 0: 
                self._delEntity(entity)
                continue
                
            if len(rlist) < n:
                for large_entity, x in zip(rlist, range(0, len(rlist) + 1)):
                    if large_entity[1][0] >= karma[0]:
                        rlist.insert(x, (entity, karma))
                        break
                else: rlist.append((entity, karma))
            else:
                for large_entity, x in zip(rlist, range(0, len(rlist) + 1)):
                    if large_entity[1][0] >= karma[0]:
                        rlist.insert(x, (entity, karma))
                        rlist.pop()
                        break
        return rlist
    
        
if __name__ == '__main__':
    db = KosBackend(':memory:', decay_time=0.01, lowercase=True)
    db.positiveKarma('Line')
    db.positiveKarma('Sindre')
    print("Line has: {k}".format(k = db.getKarma('Line')))
    print("Sindre has: {k}".format(k = db.getKarma('Sindre')))
    print(db.getAllEntities())
    sleep(60)
    db.positiveKarma('Line')
    print("Line has: {k}".format(k = db.getKarma('Line')))
    db.negativeKarma('Sindre')
    print("Sindre has: {k}".format(k = db.getKarma('Sindre')))
    print("NBest: {l}".format(l = db.getNBestList()))
    db.positiveKarma("Hermann")
    db.positiveKarma("Hermann")
    db.positiveKarma(u"Trønd")
    db.negativeKarma("Sindre")
    print("NBest: {l}".format(l = db.getNBestList(n=3)))
    print("NWorst: {l}".format(l = db.getNWorstList()))
    #sleep(60)
    print("NBest: {l}".format(l = db.getNBestList(n=3, t=(time() + 60 + (0.01 * 24 * 60 * 60)))))
    print("NWorst: {l}".format(l = db.getNWorstList()))
    db.disconnect()
    try:
        db.positiveKarma('Line')
    except DatabaseIsNotOpenError:
        print("The Database was not open, as expected")
