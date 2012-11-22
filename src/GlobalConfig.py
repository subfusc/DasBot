# -*- coding: utf-8 -*-

# General Config Options
VERBOSE = False
DEBUG = False
IRC_DEBUG = False
VERSION = 0.2
NAME = "StupidBot"
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
STARTUP_CHANNELS = ['#iskbot']

# ChannelManagerBot Config
# Not in use ATM
#PING_USERS = True
#PING_DELAY = 10 * 60

# LOGGER BOT config

LOG_FILE = 'data/irc.log'
LOG_CHANNELS = True
LOG_BUFFER_SIZE = 1

# Plugin Bot config
LOAD_PLUGINS = ["Kafe","Useless"]

# CRON JOB BOT config
START_CRON_BOT = True

# Authentication System Config
AUTHENTICATION = True
RECOVER_USERS = True
DATABASE_NAME = 'data/user_database.sql'
HASH_ROUNDS = 200
BOT_EMAIL = '' # must be set in order for the bot to send mail
SMTP_SERVER = 'localhost' # Must be changed. smtp.uio.no i believe for hosting on IFI
BOT_NICK = NAME
DOMAIN_RESTRICTION = '' # For email, if you e.g want only *uio.no domains, you write .*uio\\.no instead of ''
                        # '' is no restrictions. The domain restriction follow python regular expression rules.
EMAIL_REGISTRATION = True # Allow users to use the same username that they have on their email
FORCE_EMAIL_REGISTRATION = False # If you only want email nicks, this should be true
