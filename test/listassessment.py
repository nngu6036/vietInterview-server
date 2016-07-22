import urllib, urllib2
from data import *

token = EMPLOYER_TOKEN
# do POST
url = URL + 'admin/assessment?token=%s&lang=vi'%TOKEN
print url
rsp = urllib2.urlopen(url)
content = rsp.read()
print content
