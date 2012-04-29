# -*- coding: utf-8 -*-
from urllib import urlopen
import re
import AuthBot
import time
from GlobalConfig import *

title_re = r'<h1 id="title">\s*<a id="title" href=".*?">([^<]*)</a>\s*</h1>'
artist_re = r'''<div\s*id="artist">\s*
<div\s*class="[^"]*">[^<]*</div>\s*
<p\s*class="meta-info">\s*<a\s*href="[^"]*">(.*?)</a>\s*
</p>\s*
</div>'''

spotify_adr = r'\s*(http://open.spotify.com/[^/]*\S*)\s*'

class SpotifyExtract:

    def __init__(self):
        self.tre = re.compile(title_re)
        self.are = re.compile(artist_re, re.X)
    
    def parse_spotify(self, url):
        artist = None
        title = None
        site = urlopen(url).read()

        match = self.tre.search(site)
        if match: 
            title = match.group(1)

        match = self.are.search(site)
        if match:
            artist = match.group(1)

        return (artist, title)

    def youtube_search(self, title, artist):
        title = title.replace(" ", "+")
        artist = artist.replace(" ", "+")
        return "http://www.youtube.com/results?search_query=%s+%s" % (title, artist)

class SpotifyBot(AuthBot.AuthBot):
        
    def __init__(self, host, port, nick, ident, realname):
        super(SpotifyBot, self).__init__(host, port, nick, ident, realname)
        self.spre = re.compile(spotify_adr)
        self.spe = SpotifyExtract()
        
    def listen(self, command, msg, channel, **kwargs):
        super(SpotifyBot, self).listen(command, msg, channel, **kwargs)
        match = self.spre.search(msg)
        if match:
            result = self.spe.parse_spotify(match.group(1))
            self.msg(channel, "Check out: %s - %s" % (result[1], result[0]))
            self.msg(channel, "To make it easy: %s" % (self.spe.youtube_search(result[1], result[0])))

if __name__ == "__main__":
    HOST='irc.ifi.uio.no' #The server we want to connect to 
    PORT=6667 #The connection port which is usually 6667 
    NICK='SpotifyBot' #The bot's nickname 
    IDENT='SpotifyBot' 
    REALNAME='Ola Nordlenning' 
    OWNER='Subfusc' #The bot owner's nick 
    
    bot = SpotifyBot(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join("#isk")
    # bot.notify("#iskbot", "Ingenting e som å lig i fjorn å feske på en fin sommardag!")
    # bot.msg("#iskbot", "Dæsken så mye fesk det e i fjorn i dag!")
    bot.start()
