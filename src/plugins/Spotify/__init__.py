# -*- coding: utf-8 -*-
from urllib import urlopen
import re
import time
import tinyurl

# title_re = r'<h1 id="title">\s*<a id="title" href=".*?">([^<]*)</a>\s*</h1>'
# artist_re = r'''<div\s*id="artist">\s*
# <div\s*class="[^"]*">[^<]*</div>\s*
# <p\s*class="meta-info">\s*<a\s*href="[^"]*">(.*?)</a>\s*
# </p>\s*
# </div>'''

title_re = r'<h1\s+itemprop="name">([^<]+)</h1>'
artist_re = r'<h2>\s+by\s+<a href="[^"]+">([^<]+)</a></h2>'   

spotify_adr = r'\s*(http://open.spotify.com/[^/]*\S*)\s*'
spotify_thing = r'\s*spotify:([^:]+):(\S*)\s*'

class Plugin:
        
    def __init__(self):
        self.spre = re.compile(spotify_adr)
        self.spt = re.compile(spotify_thing)
        self.spe = SpotifyExtract()

    def check_and_msg(self, channel, result):
        if result[0] != None and result[1] != None:
            return [(0, channel, "{a} by {b}, {c} ".format(a = result[1], b = result[0], c = tinyurl.create_one(self.spe.grooveshark_search(result[1], result[0]))))]
        else:
            return [(0, channel, "Spotify Timed out??")]
        
    def listen(self, msg, channel, **kwargs):
        match = self.spre.search(msg)
        if match:
            return self.check_and_msg(channel, self.spe.parse_spotify(match.group(1)))

        match = self.spt.search(msg)
        if match:
            return self.check_and_msg(channel, self.spe.rewrite_and_parse(match.group(1), match.group(2)))

class SpotifyExtract:

    def __init__(self):
        self.tre = re.compile(title_re)
        self.are = re.compile(artist_re)

    def rewrite_and_parse(self, t, desc):
        return self.parse_spotify("http://open.spotify.com/%s/%s" % (t, desc))
        
    def parse_spotify(self, url):
        try:
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
        except:
            return None
        
    def grooveshark_search(self, title, artist):
        title = title.replace(" ", "+")
        artist = artist.replace(" ", "+")
        return "http://grooveshark.com/#!/search?q=%s+%s" % (title, artist)
    
    def youtube_search(self, title, artist):
        title = title.replace(" ", "+")
        artist = artist.replace(" ", "+")
        return "http://www.youtube.com/results?search_query=%s+%s" % (title, artist)
