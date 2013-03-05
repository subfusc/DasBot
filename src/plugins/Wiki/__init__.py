import simplemediawiki as wiki
from kitchen.text.converters import to_bytes
from sys import stderr

class Plugin(object):

    def __init__(self, *args):
        self.listeners = {}
        self.history = {}
        self.stop = {}

    def _get_changes(self, channel):
        history = self.history[channel] if channel in self.history else None
        response = None
        if len(args) == 1 and channel in self.listeners:
            response = self.listeners[channel].call({'action': 'query',
                                                     'list': 'recentchanges',
                                                     'rclimit': '5',
                                                     'rcprop': 'user|comment|title|timestamp'})
        elif len(args) == 2 and args[1] in self.listeners:
            response = self.listeners[args[1]].call({'action': 'query',
                                                     'list': 'recentchanges',
                                                     'rclimit': '5',
                                                     'rcprop': 'user|comment|title|timestamp'})
            if response:
                rlist = []
                for event in response['query']['recentchanges']:
                    rlist.append((channel, to_bytes(event['user']), 
                                  to_bytes(event['type']), to_bytes(event['comment']), 
                                  to_bytes(event['timestamp']),
                                  to_bytes(event['title']) if 'title' in event else ""))
                return rlist
                
    def _filter_new(self, channel, response):

    
    def monitor(self, args, channel, **kwargs): 
        if channel in self.stop: return
        if channel in self.history and channel in self.listeners:
            history = self.history[channel]
            
            
        
    def cmd(self, cmd, args, channel, **kwargs):
        # stderr.write("Call: " + cmd + " :: " + args + " :: " + channel + " " + str(kwargs) + "\n")
        if cmd == 'wiki':
            if not args: return [(0, channel, kwargs['from_nick'], "No arguments")]
            args = args.split() if args.find(" ") != -1 else [args]
            if args[0] == 'add' and kwargs['auth_level'] >= 50:
                if len(args) == 2:
                    self.listeners[channel] = wiki.MediaWiki(args[1])
                elif len(args) == 3:
                    if args[1][0] == '#':
                        self.listeners[args[1]] = wiki.MediaWiki(args[2])
                elif len(args) == 4:
                    self.listeners[channel] = wiki.MediaWiki(args[1])
                    if self.listeners[channel].login(args[2], args[3]):
                        return [(0, channel, kwargs['from_nick'], "Done")]
                    else: return [(0, channel, kwargs['from_nick'], "Wrong login")]
                elif len(args) == 5:
                    if args[1][0] == '#':
                        self.listeners[args[1]] = wiki.MediaWiki(args[2])
                        if self.listeners[args[1]].login(args[3], args[4]):
                            return [(0, channel, kwargs['from_nick'], "Done")]
                        else: return [(0, channel, kwargs['from_nick'], "Wrong login")]
            elif args[0] == 'del' and kwargs['auth_level'] >= 50:
                if len(args) == 1:
                    del(self.listeners[channel])
                elif len(args) == 2:
                    del(self.listeners[args[1]])
            elif args[0] == 'changes':

        

if __name__ == '__main__':
    t = Plugin()
    t.cmd('wiki', 
          'add #test http://pisk.ifi.uio.no/wiki/api.php', 
          'tull', from_nick='me', auth_level = 51)
    print(t.cmd('wiki', 'changes #test', 'tull', from_nick='me'))
    print(t.cmd('wiki', 'changes', '#test', from_nick='me'))
