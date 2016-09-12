import urllib, urllib2
from data import *

token = TOKEN
# do POST
url = URL + 'common/assignment/category?lang=en'
print url
rsp = urllib2.urlopen(url)
content = rsp.read()
print content
