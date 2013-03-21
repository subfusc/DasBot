import urllib
import urllib2

url = 'http://pastebin.com/api/api_post.php'
args = '(A + B) > C'

code = 'her er en lang line\n med noe mer greier'

values = { 'api_option':'paste',
           'api_paste_private':'1',
           'api_paste_name':args,
           'api_paste_expire_date':'10M',
           'api_dev_key':'4c59086bba061d1c49277a824599343c',
           'api_paste_code':code }

data = urllib.urlencode(values)
request = urllib2.Request(url, data)
response = urllib2.urlopen(request)
page = response.read()

print(page)
