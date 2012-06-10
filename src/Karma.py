# --*-- coding: utf-8 --*--
import sqlite3 as sql

# general
dbName = "karma.db"

# tables
TABLE_USERS = "usert"

# keys
KEY_ID = "_id"
KEY_USERNAME = "username"
KEY_KARMA = "kamount"

TABLE_CREATE_USERS = "create table if not exists " + TABLE_USERS + "(" \
	+ KEY_ID + " integer primary key autoincrement," \
	+ KEY_USERNAME + " text not null," \
	+ KEY_KARMA + " integer not null)" 

class Karma:
	"""Karma functionality"""
	
	# Checks if user is already in the database
	def userExist(self, username):
		connection = sql.connect(dbName)

		cursor = connection.cursor()

		cursor.execute("select " + KEY_ID + " from " + TABLE_USERS + " where " + KEY_USERNAME + " = \'" + username + "\'")

		result = cursor.fetchone()

		if result:
			return True
		else:
			return False

	# Adds user to database if not already there
	def addUser(self, username):
		if not self.userExist(username):
			connection = sql.connect(dbName)

			cursor = connection.cursor()

			cursor.execute("insert into " + TABLE_USERS + " (" + KEY_USERNAME + "," + KEY_KARMA + ") values(\'" + username + "\', 0)")

			connection.commit()

			connection.close()

	# Adds karma to a user, and creates the giver and reciever if not already there
	def addKarma(self, fromUser, toUser):
		if not self.userExist(fromUser):
			self.addUser(fromUser)
		if not self.userExist(toUser):
			self.addUser(toUser)

		connection = sql.connect(dbName)

		cursor = connection.cursor()

		cursor.execute("update " + TABLE_USERS + " set " + KEY_KARMA + "=" + KEY_KARMA + "+1" + " where " + KEY_USERNAME + " = \'" + toUser + "\'")

		connection.commit()

		connection.close()

	# Removes karma from a user, and creates the taker and reciever if not already there
	def delKarma(self, fromUser, toUser):
		if not self.userExist(fromUser):
			self.addUser(fromUser)
		if not self.userExist(toUser):
			self.addUser(toUser)

		connection = sql.connect(dbName)

		cursor = connection.cursor()

		cursor.execute("update " + TABLE_USERS + " set " + KEY_KARMA + "=" + KEY_KARMA + "-1" + " where " + KEY_USERNAME + " = \'" + toUser + "\'")

		connection.commit()

		connection.close()

	# Fetches N number of top karma recievers
	def getTopUsers(self, limit):
		if limit > 0:
			connection = sql.connect(dbName)

			cursor = connection.cursor()

			cursor.execute("select " + KEY_USERNAME + "," + KEY_KARMA + " from " + TABLE_USERS + " order by " + KEY_KARMA + " desc limit " + str(limit))

			result = cursor.fetchall()

			connection.close()

			return result

	# Creates database and tables if not already there
	def testOrCreateDb(self):
		
		connection = sql.connect(dbName)

		cursor = connection.cursor()

		cursor.execute(TABLE_CREATE_USERS)

		connection.commit()

		connection.close()

	# Constructor
	def __init__(self):
		self.testOrCreateDb()
