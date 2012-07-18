# -*- coding: utf-8 -*-
import sqlite3 as sql

# general
dbName = "data/karma.sql"

# tables
TABLE_USERS = "usert"

# keys
KEY_ID = "_id"
KEY_USERNAME = "username"
KEY_KARMA = "kamount"

TABLE_CREATE_USERS = "create table if not exists " + TABLE_USERS + "(" \
+ KEY_ID + " integer primary key autoincrement," \
+ KEY_USERNAME + " text not null," \
+ KEY_KARMA + " integer not null, unique (" + KEY_USERNAME + "))" 

class Karma(object):
    def __init__(self):
        self.db = sql.connect(dbName)
        self.testOrCreateDb()

    def __del__(self):
        self.db.close()

	# Creates database and tables if not already there
    def testOrCreateDb(self):
        self.db.execute(TABLE_CREATE_USERS)
        self.db.commit()

	# Checks if user is already in the database
    def userExist(self, username):
        self.db.commit()
        cursor = self.db.execute("select " + KEY_ID + " from " + TABLE_USERS + " where " + KEY_USERNAME + " = \'" + username + "\'")
        result = cursor.fetchone()

        if result:
			return True
        else:
			return False

	# Adds user to database if not already there
    def addUser(self, username):
        self.db.execute("insert into " + TABLE_USERS + " (" + KEY_USERNAME + "," + KEY_KARMA + ") values(\'" + username + "\', 0)")
        self.db.commit()

	# Adds karma to a user, and creates the giver and reciever if not already there
    def addKarma(self, toUser):
        if not self.userExist(toUser):
            self.addUser(toUser)
        self.db.execute("update " + TABLE_USERS + " set " + KEY_KARMA + "=" + KEY_KARMA + "+1" + " where " + KEY_USERNAME + " = \'" + toUser + "\'")

	# Removes karma from a user, and creates the taker and reciever if not already there
    def delKarma(self, toUser):
		if not self.userExist(toUser):
			self.addUser(toUser)
		self.db.execute("update " + TABLE_USERS + " set " + KEY_KARMA + "=" + KEY_KARMA\
                        + "-1" + " where " + KEY_USERNAME + " = \'" + toUser + "\'")

	# Fetches N number of top karma recievers
    def getTopUsers(self, limit):
        if limit > 0:
            self.db.commit()
            cursor = self.db.execute("select " + KEY_USERNAME + "," + KEY_KARMA + \
                                     " from " + TABLE_USERS + " order by " + KEY_KARMA\
                                     + " desc limit " + str(limit))

            return cursor.fetchall()

	# Fetches a spesific users karma
    def getUserKarma(self, username):
        self.db.commit()
        cursor = self.db.execute("select " + KEY_KARMA + " from " + TABLE_USERS + " where " + KEY_USERNAME\
                                 + "=\'" + username + "\'")
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

