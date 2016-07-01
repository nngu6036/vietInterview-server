import urllib, urllib2
from data import *

token = TOKEN
# do POST
url = URL + 'admin/question/category?token=%s'%token
print url
rsp = urllib2.urlopen(url)
content = rsp.read()
print content