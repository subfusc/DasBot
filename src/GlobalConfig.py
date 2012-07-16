# -*- coding: utf-8 -*-

# General Config Options
VERBOSE = True
DEBUG = True
VERSION = 0.2
NAME = "TestBot"
COMMAND_CHAR = "!"
HELP_CHAR = '?'

# IRCbot config
CHANGE_RUNTIME_USER = False
UID = 1000
GID = 1000
HOST = "irc.ifi.uio.no"
PORT = 6667
NICK = NAME
IDENT = NAME
REAL_NAME = NAME
OWNER = "Subfusc"
RAWLOG = False
RAWLOG_FILE = "IRC.log"

# ChannelManagerBot Config
PING_USERS = True
PING_DELAY = 10 * 60

# LOGGER BOT config
LOG_FILE = 'irc.log'
LOG_BUFFER_SIZE = 1

# Authentication System Config
AUTHENTICATION = False
RECOVER_USERS = True
DATABASE_NAME = 'user_database.sql'
HASH_ROUNDS = 200
BOT_EMAIL = ''
BOT_NICK = NAME
